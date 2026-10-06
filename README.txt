SVAASA payment regression fix

Cause:
The refund-groundwork package was built on top of the order-lifecycle package, whose payments/views.py was the pre-v2 version. That version omitted the two explicit order.payment_status = "paid" assignments added by payment-state-fix-v2. This caused 3 existing payment regression tests to fail.

This patch contains ONLY backend/payments/views.py from the already-tested payment-state-fix-v2 package. It restores those two assignments while preserving the new Refund model/admin/refunds service and migration.

Apply:
1. Extract this ZIP into C:\Users\OMEN\Desktop\SVASSA and allow overwrite.
2. From backend with venv active run:
   python manage.py check
   python manage.py test payments
   python manage.py test

Expected:
- payment tests: 23/23 passing
- full suite: 51/51 passing

Do NOT run migrations for this patch; it contains no migration.
Do NOT delete db.sqlite3.
