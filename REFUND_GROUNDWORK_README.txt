SVAASA — Refund Groundwork Update

This package builds the refund foundation on top of the already-tested order lifecycle.

What it adds:
- Refund model with durable status, amount, reason, gateway refund ID, audit users and timestamps.
- Admin Refund screen.
- Refund request creation only for cancelled + paid + captured orders.
- Idempotent pending/processing request creation.
- Refund lifecycle:
    pending -> processing -> processed
    pending -> cancelled
    processing -> failed | cancelled
    failed -> processing
- Marking a refund processed requires a gateway refund ID and changes:
    Payment.status = refunded
    Order.payment_status = refunded
- Failed/cancelled refund attempts do NOT falsely mark the order refunded.
- Customer order API exposes refund status.
- Staff notifications are created for refund request/status changes.
- Full refund only for now. Partial refunds are intentionally deferred.
- IMPORTANT: this is groundwork/manual confirmation. It does NOT call Razorpay's live refund API yet.

Recommended browser test after applying:
1. Open the already-cancelled paid order SH-C89A0DDEFD.
2. In Django admin, open Refunds -> Add Refund.
3. Select SH-C89A0DDEFD, reason "Order cancellation", and note "Customer cancellation — refund required."
4. Save. Verify a Pending refund is created for the captured payment amount.
5. Do NOT mark it Processed using a fake ID in the real database unless you are intentionally testing state transitions. For the real order, leave it Pending/Processing until an actual Razorpay refund is executed.
6. Later, the next milestone will connect Processing to Razorpay's refund API and make the gateway refund ID come from Razorpay.

Apply from the project root:
1. Back up your working tree if desired.
2. Extract this ZIP into the project root (C:\Users\OMEN\Desktop\SVASSA) with overwrite enabled.
3. Activate the venv.
4. Run:
   cd backend
   python manage.py check
   python manage.py migrate
   python manage.py test payments
   python manage.py test
5. Do not delete db.sqlite3.
