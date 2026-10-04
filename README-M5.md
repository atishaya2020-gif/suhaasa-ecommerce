# SUHAASA Commerce Milestone 5 — Payments

This is a **patch for the existing SUHAASA project**, not a replacement project.

## Preserve

- Keep your existing `db.sqlite3`.
- Keep your existing products, accounts, commerce, media, and admin data.
- Keep the approved V15 UI.

## Copy from this milestone

1. Copy `backend/payments/` into your existing `backend/`.
2. Replace `backend/config/settings.py` with this milestone version.
3. Replace `backend/config/urls.py` with this milestone version.
4. Replace `backend/orders/models.py` and `backend/orders/views.py` with these versions.
5. Replace `frontend/src/main.jsx` with this milestone version.
6. Copy the `.env.example` values into your existing `backend/.env`; do not commit secrets.

## Install Razorpay SDK

```powershell
python -m pip install razorpay
```

## Configure TEST mode

Set these in `backend/.env`:

```text
RAZORPAY_KEY_ID=rzp_test_...
RAZORPAY_KEY_SECRET=...
RAZORPAY_WEBHOOK_SECRET=...
```

The secret stays on Django. Only the public Key ID is returned to the browser.

## Run

```powershell
python manage.py migrate
python manage.py runserver
```

In the frontend terminal:

```powershell
npm run dev
```

## New flow

`Checkout → Create SUHAASA order → Django creates Razorpay order → Razorpay Checkout → server verifies signature + captured status → order becomes Paid → cart clears.`

If payment is cancelled or fails, the SUHAASA order remains pending/failed and the cart is retained so the customer can retry.

## Important quantity regression check

The product detail and quick-view quantity defaults are explicitly `1`. Before sign-off, verify:

- a fresh product shows quantity `1`;
- one Add to Bag click creates quantity `1`;
- increasing quantity to `2` creates/updates quantity `2` only when requested;
- refreshing the page does not double quantities.

## Security

Razorpay's current Python integration requires creating the gateway order on the server, passing its order ID to Checkout, verifying the returned signature on the server, and checking captured payment status. Webhook signatures are also validated server-side. Use Test Mode before Live Mode and HTTPS in production.
