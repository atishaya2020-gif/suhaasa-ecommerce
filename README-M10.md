# SUHAASA Commerce Milestone 10 — Account & Order Experience

This milestone upgrades the existing authenticated customer flow without changing the approved V15 visual baseline.

## Included
- Account dashboard with profile, orders and saved addresses.
- Safe profile editing; sign-in email remains read-only.
- Saved addresses with add/edit/remove/default-address handling.
- Order list with status and payment state.
- Full order details with item snapshots, shipping address, totals and payment information.
- Order status timeline.
- Reorder endpoint that uses current product/variant prices and respects current stock.
- Checkout can prefill the customer's default saved address.
- Order confirmation now surfaces the order number, item count, delivery method and payment confirmation.
- Backend ownership checks for profiles, addresses, orders and reorder operations.
- `Order.address_line2` snapshot field added with migration `0002_order_address_line2`.

## Backend endpoints
- `GET/PATCH /api/auth/me/`
- `GET/POST /api/auth/addresses/`
- `PATCH/DELETE /api/auth/addresses/<id>/`
- `GET /api/orders/`
- `GET /api/orders/<order_number>/`
- `POST /api/orders/<order_number>/reorder/`

## Apply
```powershell
cd C:\Users\OMEN\Desktop\suhaasa-build-integrated\backend
.\.venv\Scripts\Activate.ps1
python manage.py makemigrations
python manage.py migrate
python manage.py check
python manage.py test accounts orders payments
```

Then start Django and the existing V15 frontend normally.

## Important
Do not replace the database, media, product catalogue, Razorpay credentials, or approved V15 design. Keep `.env` private.
