SVAASA — Payment State Regression Fix v2

Purpose
-------
Apply the next payment/lifecycle hardening update on top of the already-applied
SVAASA Order Lifecycle update.

This fixes the regression where a successful Razorpay payment could set the
Payment record to `captured` and the Order status to `placed`, but leave
Order.payment_status as `pending`.

Changes
-------
1. `backend/payments/views.py`
   - Payment verification now explicitly persists `order.payment_status = "paid"`.
   - Razorpay `payment.captured` / `order.paid` webhook handling now explicitly
     persists `order.payment_status = "paid"`.
   - Existing idempotency, inventory reservation consumption, and guest-cart
     cleanup behavior is preserved.
   - Late capture after an already-released reservation remains a
     `reconciliation_required` 409 and does not fulfill the order.

2. `backend/payments/test_payment_capture_regression.py`
   - Regression coverage for capture webhook -> paid + placed.
   - Duplicate capture remains idempotent with no second inventory change.
   - Payment verification -> paid + placed.
   - Late capture after reservation release -> reconciliation_required, no
     fulfillment, no second inventory change.

Important
---------
- Do NOT delete or replace `db.sqlite3`.
- Do NOT change the V15 storefront.
- This package is intended to be applied over the current local project after
  the SVAASA Order Lifecycle update has already been applied.

PowerShell steps
----------------
From:
  C:\Users\OMEN\Desktop\SVASSA\backend

1. Back up the two target files if desired.
2. Extract the package contents into the project root so that `backend/...`
   lands in your project as `backend/...` only if your extraction target is the
   project root. If you extract directly into the backend directory, copy the
   files from the package's `backend` folder instead.

Recommended safer approach: extract the ZIP somewhere temporary and copy only:
  backend\payments\views.py
  backend\payments\test_payment_capture_regression.py

Then run:
  .\.venv\Scripts\Activate.ps1
  python manage.py check
  python manage.py test payments
  python manage.py test

Expected result after applying the fix:
  - The previous `PaymentStateTransitionTests.test_duplicate_capture_webhook_is_idempotent`
    regression passes.
  - Full suite passes with the lifecycle tests plus the new regression tests.

Do not commit/push until the full suite is green.
