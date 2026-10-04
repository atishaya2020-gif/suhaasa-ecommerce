# SUHAASA Commerce Milestone 6 — Auth-Required Checkout + My Orders

This is a patch for the existing SUHAASA integrated project after Milestone 5.

## What changed

### 1. Login is mandatory before purchase
- `POST /api/orders/create/` now requires JWT authentication.
- Razorpay order creation and payment verification also require JWT authentication.
- The payment ownership check only accepts orders belonging to the authenticated user.
- Frontend checkout is gated behind login/register.
- Guest shoppers can still browse, wishlist, and build a cart.
- Guest cart contents are migrated into the account when the customer logs in/registers before checkout.

### 2. Successful payment clears the correct cart
Payment verification now clears the cart attached to the paid order:

```python
if order.session_id:
    order.session.cart_items.all().delete()
```

It no longer relies on the guest token from the payment-verification request.

The Razorpay webhook already follows the same order-session cleanup path.

### 3. Customer order history
Logged-in customers now have:

**Account → My orders**

The UI shows:
- order number
- date
- total
- order status
- payment status
- purchased items
- variants and quantities
- line totals

The existing backend endpoints remain protected by `IsAuthenticated` and only return the current user's orders.

### 4. Guest-order migration safeguard
If a customer had an older guest order and then logs into/registers using that same guest session, eligible guest orders are associated with the authenticated account before the guest session is removed.

This is mainly a backward-compatibility safeguard; new orders are authenticated-only.

### 5. Regression tests
Added API tests confirming anonymous users cannot create orders or access order history, and cannot create/verify Razorpay payments.

## Files to replace

Copy these files into the existing integrated project:

```text
backend/commerce/views.py
backend/orders/views.py
backend/orders/tests.py
backend/payments/views.py
backend/payments/tests.py
frontend/src/main.jsx
frontend/src/styles.css
```

No new database migration is required for this milestone.

## Apply

From the integrated project:

```powershell
cd C:\Users\OMEN\Desktop\suhaasa-build-integrated\backend
.\.venv\Scripts\Activate.ps1
python manage.py check
python manage.py test orders payments
```

Then start Django normally:

```powershell
python manage.py runserver
```

And from the frontend:

```powershell
cd C:\Users\OMEN\Desktop\suhaasa-build-integrated\frontend
npm run dev
```

## Manual acceptance test

1. Sign out / clear the current access token.
2. Add a product to the bag while logged out.
3. Click **Proceed to checkout**.
4. Confirm SUHAASA asks for login/register instead of opening payment.
5. Log in or register.
6. Confirm the existing guest cart remains after login.
7. Complete checkout with Razorpay Test Mode.
8. Confirm the order is `placed` and payment is `paid`.
9. Confirm the persistent cart is empty after successful payment.
10. Refresh the site and confirm the cart remains empty.
11. Open account → **My orders** and confirm the order appears.
12. Cancel/fail a separate test payment and confirm its cart remains available for retry.
13. Confirm a logged-out direct request to `/api/orders/create/` is rejected.

## Important

Do not delete the existing database, products, media, accounts, or Razorpay `.env` values when applying this patch.

This milestone does not change the approved V15 visual baseline beyond the new account/order/checkout states needed for the commerce flow.
