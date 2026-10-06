SVAASA — Live Razorpay Refund Integration

This patch builds on the existing refund groundwork and connects it to Razorpay's Normal Refund API.

WHAT IT DOES
- Uses Razorpay's refund endpoint for the captured payment.
- Sends a durable X-Refund-Idempotency key on every refund request.
- Network/timeout/5xx/409-while-processing outcomes remain Processing and reuse the SAME key.
- Definitive 4xx gateway errors become Failed.
- A successful gateway response with status pending/processed is reconciled locally.
- refund.created / refund.processed / refund.failed webhook events update the local refund.
- A processed full refund changes Payment.status to refunded and Order.payment_status to refunded.
- Duplicate refund webhooks are harmless because the gateway refund ID is the durable identity.
- Admin has explicit actions to process selected refunds through Razorpay or sync a known gateway refund.
- The existing 4,398 INR refund for SH-C89A0DDEFD remains Pending until you deliberately process it.

IMPORTANT
- The current integration supports FULL refunds only, matching the existing groundwork. Partial refunds can be added later with cumulative refund accounting.
- The Process action is a REAL gateway call. Do not click it for a live transaction unless you intend to refund it.
- Before production, configure Razorpay Dashboard webhooks for refund.created, refund.processed and refund.failed and point them to the existing webhook endpoint.
- Keep RAZORPAY_KEY_SECRET and RAZORPAY_WEBHOOK_SECRET out of Git.

VERIFY LOCALLY
cd C:\Users\OMEN\Desktop\SVASSA\backend
.\.venv\Scripts\Activate.ps1
python manage.py check
python manage.py migrate
python manage.py test payments
python manage.py test

EXPECTED TEST COUNT
The existing suite was 51 tests before this patch. This patch adds 7 refund integration tests, so the full suite should be 58 tests when combined with the current codebase.

REAL TEST SEQUENCE
1. Run all tests first.
2. Confirm SH-C89A0DDEFD is cancelled + paid and its Refund is Pending.
3. Only when you intentionally want to issue the refund, select that Refund in SVAASA Admin and choose:
   Action -> Process selected refunds via Razorpay -> Run.
4. If Razorpay returns processed, the Refund becomes Processed and Payment/Order payment status becomes Refunded.
5. If Razorpay returns pending, the Refund becomes Processing and webhook/sync will complete it later.
6. If the request times out, leave it Processing and retry with the SAME idempotency key; do not create another refund record.
