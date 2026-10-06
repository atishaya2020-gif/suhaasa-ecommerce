SVAASA — Order Lifecycle Update

This package implements the next order-lifecycle milestone from the stable
checkpoint c9e5266.

Lifecycle:
pending_payment -> placed -> processing -> shipped -> delivered

Cancellation:
pending_payment -> cancelled
placed -> cancelled
processing -> cancelled

Rules:
- shipped and delivered are terminal for the current milestone.
- Invalid jumps are rejected.
- Pending-payment cancellation releases reserved stock and marks payment failed.
- Paid cancellation restores inventory but DOES NOT falsely mark the payment refunded.
  It leaves payment_status=paid and creates a notification saying refund action is
  still required. Actual Razorpay refund integration remains a later milestone.
- Every lifecycle transition creates OrderStatusHistory.
- Staff receive an in-app notification for each lifecycle transition.
- Customer order APIs now return status_history.
- Django admin exposes only valid next statuses and an optional status note.
- Orders can no longer be manually created from Django admin; they originate from checkout.

Apply from the project root:
1. Back up your current working tree if needed.
2. Extract this ZIP into C:\Users\OMEN\Desktop\SVASSA with overwrite enabled.
3. Activate the venv.
4. Run:
   python manage.py check
   python manage.py migrate
   python manage.py test orders
   python manage.py test
5. Only after all tests pass, inspect /admin/orders/order/ in the browser.

Do NOT delete db.sqlite3.
