# SUHAASA Commerce — Milestone 4

This milestone adds the real checkout/order pipeline underneath the approved V15 storefront.

## Added
- Django `orders` app with Order and OrderItem models.
- Backend-calculated subtotal, shipping and total.
- Standard shipping: free at ₹1,499+, otherwise ₹99.
- Express shipping: ₹149.
- Stock validation and atomic inventory decrement when an order is created.
- Product/variant price and identity snapshots on each order item.
- Guest and authenticated order creation.
- Authenticated order history/detail APIs.
- Django Admin order management.
- Frontend checkout now creates a real backend order instead of only showing a frontend preview.
- Payment status starts as `pending`; no payment gateway is connected yet.

## Backend
```powershell
cd backend
.\.venv\Scripts\Activate.ps1
python manage.py migrate
python manage.py runserver
```

## Frontend
```powershell
cd frontend
npm install
npm run dev
```

Do not delete the existing `db.sqlite3` when applying this patch.
