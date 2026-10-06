import uuid
from decimal import Decimal

import requests
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from notifications.services import create_notification

from .models import Payment, Refund


REFUND_TRANSITIONS = {
    "pending": {"processing", "cancelled"},
    "processing": {"processed", "failed", "cancelled"},
    "processed": set(),
    "failed": {"processing", "cancelled"},
    "cancelled": set(),
}


def _notify_staff(refund, title, message):
    from django.contrib.auth import get_user_model

    User = get_user_model()
    for recipient in User.objects.filter(is_staff=True):
        create_notification(
            recipient=recipient,
            kind="payment",
            title=title,
            message=message,
            link=f"/admin/payments/refund/{refund.pk}/change/",
            dedupe_key=f"refund:{refund.pk}:{refund.status}",
        )


def create_refund_request(*, order_id, requested_by=None, reason="cancellation", note=""):
    with transaction.atomic():
        from orders.models import Order

        order = Order.objects.select_for_update().get(pk=order_id)
        payment = Payment.objects.select_for_update().filter(order=order).first()

        if order.payment_status != "paid" or not payment or payment.status != "captured":
            raise ValidationError("A refund can only be requested for a captured, paid order.")

        if order.status != "cancelled":
            raise ValidationError("Refund requests are currently available only for cancelled orders.")

        active = order.refunds.filter(status__in={"pending", "processing"}).first()
        if active:
            return active

        processed = order.refunds.filter(status="processed").first()
        if processed:
            raise ValidationError("This order has already been refunded.")

        refund = Refund.objects.create(
            order=order,
            amount=payment.amount,
            currency=payment.currency,
            reason=reason,
            note=note,
            status="pending",
            requested_by=requested_by,
        )

        _notify_staff(
            refund,
            "Refund request created",
            f"{order.order_number} has a pending refund request for ₹{refund.amount:,.2f}.",
        )
        return refund


def transition_refund(refund, new_status, *, changed_by=None, gateway_refund_id="", raw_response=None):
    """Transition a refund through the local refund state machine.

    Kept as the public service entry point used by the refund groundwork tests
    and any non-gateway admin/service callers. Gateway-specific completion is
    delegated to the same locked helper used by Razorpay webhooks.
    """
    with transaction.atomic():
        if not isinstance(refund, Refund):
            refund = Refund.objects.select_for_update().select_related("order").get(pk=refund)
        else:
            refund = (
                Refund.objects.select_for_update()
                .select_related("order")
                .get(pk=refund.pk)
            )

        new_status = str(new_status or "").lower().strip()
        if new_status not in REFUND_TRANSITIONS:
            raise ValidationError(f"Unknown refund status: {new_status}.")
        if new_status == refund.status:
            return refund
        if new_status not in REFUND_TRANSITIONS.get(refund.status, set()):
            raise ValidationError(
                f"Invalid refund transition: {refund.status} -> {new_status}."
            )

        if new_status == "processed":
            payment = Payment.objects.select_for_update().filter(order=refund.order).first()
            return _mark_processed_locked(
                refund,
                payment,
                changed_by=changed_by,
                gateway_refund_id=gateway_refund_id or refund.gateway_refund_id,
                raw_response=raw_response,
            )

        refund.status = new_status
        if gateway_refund_id:
            refund.gateway_refund_id = gateway_refund_id
        if raw_response is not None:
            refund.raw_response = raw_response
        if changed_by is not None and new_status == "failed":
            refund.processed_by = changed_by
        update_fields = ["status", "gateway_refund_id", "raw_response", "processed_by", "updated_at"]
        refund.save(update_fields=update_fields)

        _notify_staff(
            refund,
            "Refund status updated",
            f"{refund.order.order_number} refund is now {refund.get_status_display().lower()}.",
        )
        return refund


def _mark_processed_locked(refund, payment, *, changed_by=None, gateway_refund_id="", raw_response=None):
    if not payment or payment.status not in {"captured", "refunded"}:
        raise ValidationError("Only a captured payment can be marked refunded.")

    expected = Decimal(payment.amount)
    if Decimal(refund.amount) != expected:
        raise ValidationError("The current live refund integration supports full refunds only.")

    if not gateway_refund_id.strip():
        raise ValidationError("A Razorpay refund ID is required before marking a refund processed.")

    refund.gateway_refund_id = gateway_refund_id.strip()
    refund.processed_by = changed_by or refund.processed_by
    refund.processed_at = timezone.now()
    refund.status = "processed"
    refund.raw_response = raw_response or refund.raw_response or {}
    refund.save(update_fields=[
        "status", "gateway_refund_id", "processed_by", "processed_at",
        "raw_response", "updated_at",
    ])

    if payment.status != "refunded":
        payment.status = "refunded"
        payment.save(update_fields=["status", "updated_at"])

    order = refund.order
    if order.payment_status != "refunded":
        order.payment_status = "refunded"
        order.save(update_fields=["payment_status", "updated_at"])

    _notify_staff(
        refund,
        "Refund completed",
        f"{order.order_number} refund of ₹{refund.amount:,.2f} was processed by Razorpay.",
    )
    return refund


def _mark_gateway_status_locked(refund, gateway_status, *, gateway_refund_id="", raw_response=None):
    payment = Payment.objects.select_for_update().filter(order=refund.order).first()
    gateway_status = (gateway_status or "").lower()

    if gateway_refund_id:
        refund.gateway_refund_id = gateway_refund_id
    if raw_response is not None:
        refund.raw_response = raw_response

    if gateway_status == "processed":
        return _mark_processed_locked(
            refund,
            payment,
            gateway_refund_id=gateway_refund_id or refund.gateway_refund_id,
            raw_response=raw_response,
        )

    if gateway_status == "failed":
        refund.status = "failed"
    else:
        refund.status = "processing"

    refund.save(update_fields=["status", "gateway_refund_id", "raw_response", "updated_at"])
    _notify_staff(
        refund,
        "Refund status updated",
        f"{refund.order.order_number} Razorpay refund is now {refund.get_status_display().lower()}.",
    )
    return refund


def request_razorpay_refund(refund_id, *, changed_by=None):
    """Create the real Razorpay normal refund using a durable idempotency key.

    Network/5xx/409-while-processing errors leave the refund in Processing so a
    retry can safely reuse the same idempotency key. Definitive 4xx failures are
    marked Failed. A successful Razorpay response is reconciled immediately.
    """
    with transaction.atomic():
        refund = Refund.objects.select_for_update().select_related("order").get(pk=refund_id)
        payment = Payment.objects.select_for_update().filter(order=refund.order).first()

        if not payment or payment.status != "captured" or refund.order.payment_status != "paid":
            raise ValidationError("Refund requires a captured, paid order.")
        if refund.order.status != "cancelled":
            raise ValidationError("Only cancelled orders can be refunded currently.")
        if refund.status == "processed":
            return refund
        if refund.status == "cancelled":
            raise ValidationError("This refund request has been cancelled.")

        if refund.status == "failed":
            refund.idempotency_key = str(uuid.uuid4())

        amount_paise = int((Decimal(refund.amount) * 100).quantize(Decimal("1")))
        if amount_paise <= 0:
            raise ValidationError("Refund amount must be greater than zero.")

        refund.status = "processing"
        refund.raw_response = {
            **(refund.raw_response or {}),
            "local": {"action": "refund_requested", "at": timezone.now().isoformat()},
        }
        refund.save(update_fields=["status", "idempotency_key", "raw_response", "updated_at"])

        _notify_staff(
            refund,
            "Refund sent to Razorpay",
            f"{refund.order.order_number} refund of ₹{refund.amount:,.2f} was submitted to Razorpay.",
        )

        url = f"https://api.razorpay.com/v1/payments/{payment.gateway_payment_id}/refund"
        payload = {"amount": amount_paise, "receipt": refund.order.order_number}
        headers = {
            "Content-Type": "application/json",
            "X-Refund-Idempotency": refund.idempotency_key,
        }

        try:
            response = requests.post(
                url,
                auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET),
                json=payload,
                headers=headers,
                timeout=20,
            )
            try:
                data = response.json()
            except ValueError:
                data = {"http_status": response.status_code, "text": response.text[:1000]}
        except requests.RequestException as exc:
            # Unknown gateway outcome: retain Processing and the SAME idempotency key.
            refund.raw_response = {"exception": str(exc)}
            refund.save(update_fields=["raw_response", "updated_at"])
            return refund

        if 200 <= response.status_code < 300:
            refund.raw_response = data
            gateway_refund_id = str(data.get("id", "")).strip()
            gateway_status = str(data.get("status", "pending")).lower()
            if not gateway_refund_id:
                # Successful response without an id is not safe to treat as complete.
                refund.save(update_fields=["raw_response", "updated_at"])
                return refund
            return _mark_gateway_status_locked(
                refund,
                gateway_status,
                gateway_refund_id=gateway_refund_id,
                raw_response=data,
            )

        # 409 may mean the same idempotent request is still being processed.
        if response.status_code == 409:
            refund.raw_response = data
            refund.save(update_fields=["raw_response", "updated_at"])
            return refund

        refund.status = "failed"
        refund.raw_response = data
        refund.processed_by = changed_by
        refund.save(update_fields=["status", "raw_response", "processed_by", "updated_at"])
        _notify_staff(
            refund,
            "Refund failed",
            f"{refund.order.order_number} Razorpay refund failed with HTTP {response.status_code}.",
        )
        return refund


def sync_razorpay_refund(refund_id, *, changed_by=None):
    with transaction.atomic():
        refund = Refund.objects.select_for_update().select_related("order").get(pk=refund_id)
        if not refund.gateway_refund_id:
            raise ValidationError("There is no Razorpay refund ID to sync yet.")

        response = requests.get(
            f"https://api.razorpay.com/v1/refunds/{refund.gateway_refund_id}",
            auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET),
            timeout=20,
        )
        try:
            data = response.json()
        except ValueError:
            data = {"http_status": response.status_code, "text": response.text[:1000]}

        if not 200 <= response.status_code < 300:
            refund.raw_response = data
            refund.save(update_fields=["raw_response", "updated_at"])
            raise ValidationError(f"Razorpay refund lookup failed with HTTP {response.status_code}.")

        return _mark_gateway_status_locked(
            refund,
            data.get("status", "pending"),
            gateway_refund_id=data.get("id", refund.gateway_refund_id),
            raw_response=data,
        )


def apply_refund_webhook(*, event, refund_entity):
    gateway_refund_id = str(refund_entity.get("id", "")).strip()
    if not gateway_refund_id:
        return None

    with transaction.atomic():
        refund = (
            Refund.objects.select_for_update()
            .select_related("order")
            .filter(gateway_refund_id=gateway_refund_id)
            .first()
        )
        if not refund:
            return None

        status_value = str(refund_entity.get("status", "")).lower()
        if event == "refund.processed":
            status_value = "processed"
        elif event == "refund.failed":
            status_value = "failed"
        elif event == "refund.created" and status_value == "processed":
            status_value = "processed"

        return _mark_gateway_status_locked(
            refund,
            status_value or "pending",
            gateway_refund_id=gateway_refund_id,
            raw_response=refund_entity,
        )
