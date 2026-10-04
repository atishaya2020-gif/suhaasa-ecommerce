# SUHAASA Milestone 5 — Razorpay payments

This milestone connects the existing Django order flow to Razorpay Standard Checkout.

## Install

```powershell
python -m pip install razorpay
```

## Configure test credentials

Copy `backend/.env.example` to `backend/.env` and fill in Razorpay **Test Mode** credentials. Keep the secret key server-side only.

## Migrate and run

```powershell
python manage.py migrate
python manage.py runserver
```

The frontend loads Razorpay Checkout only when the customer starts payment. The browser receives the public Key ID and a server-created Razorpay order ID; the secret remains on Django.

## Payment flow

1. SUHAASA creates its order and validates stock/pricing on Django.
2. Django creates a Razorpay Order using the backend total.
3. The browser opens Razorpay Standard Checkout.
4. Razorpay returns payment ID, order ID, and signature.
5. Django verifies the signature server-side.
6. Only after successful verification is the SUHAASA order marked paid and the cart cleared.
7. Razorpay webhooks can update payment state asynchronously.

For production, configure HTTPS, webhook signature validation, test the full flow in Razorpay Test Mode, then switch to Live Mode. Never put `RAZORPAY_KEY_SECRET` in Vite/frontend environment variables.
