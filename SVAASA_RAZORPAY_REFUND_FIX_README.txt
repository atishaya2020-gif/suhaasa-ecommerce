SVAASA — Razorpay Refund Integration Compatibility Fix

This is a corrective patch for the first Razorpay refund integration package.

Fixes:
1. Restores the public transition_refund() service expected by the existing refund groundwork tests.
2. Makes the idempotency-key regression assertion type-safe because Django returns a UUID object from the model default while storing it as text.

No migration is required. Do NOT delete db.sqlite3.

Apply by extracting into:
C:\Users\OMEN\Desktop\SVASSA

Then run from backend:
.\.venv\Scripts\Activate.ps1
python manage.py check
python manage.py test payments
python manage.py test

Expected result:
- payments: 30 tests (23 existing + 7 refund integration)
- full suite: 58 tests
- all green

Do NOT process the pending SH-C89A0DDEFD refund through Razorpay until the tests are green and you explicitly intend to issue the real refund.
