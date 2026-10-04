# SUHAASA Commerce Milestone 8 — Commerce Regression Fix

This is the next patch for the existing integrated SUHAASA project. It rolls forward the authenticated-checkout and customer-order flow from Milestone 6 and the Add-to-Bag quantity protection from Milestone 7, while fixing the frontend runtime regression introduced by Milestone 7.

## Fix included

### Frontend runtime error
Milestone 7 introduced `useRef()` for the Add-to-Bag in-flight lock but did not import `useRef`. That caused the production UI to render a blank page with:

`Uncaught ReferenceError: useRef is not defined`

Milestone 8 adds the missing React import.

### Purchase/auth rules retained
- Customers must be signed in before creating an order or starting payment.
- Guest users can browse, wishlist, and build a cart.
- Guest cart contents can migrate into the account on login/register.
- Customer accounts have **My orders**.

### Quantity protection retained
- Product-detail quantity defaults to **1**.
- Quick-view quantity defaults to **1**.
- A single Add-to-bag action submits exactly the selected quantity.
- Rapid/double clicks are protected by a variant/size in-flight lock.
- A second deliberate Add-to-bag action intentionally increases the existing line quantity.
- Cart +/- remains the explicit way to change cart quantity.

## Files to replace

Copy these files into the existing integrated project:

```text
backend/commerce/views.py
frontend/src/main.jsx
```

No database migration is required.

## Apply

From the integrated project:

```powershell
cd C:\Users\OMEN\Desktop\suhaasa-build-integrated\backend
.\.venv\Scripts\Activate.ps1
python manage.py check
```

Then restart Django:

```powershell
python manage.py runserver
```

In a second terminal:

```powershell
cd C:\Users\OMEN\Desktop\suhaasa-build-integrated\frontend
npm run dev
```

## Regression test

1. Open the site and confirm the blank page/runtime error is gone.
2. Clear the current test cart through the UI.
3. Open a product detail page and confirm quantity is **1**.
4. Click **Add to bag once**; cart quantity must be **1**.
5. Refresh; quantity must remain **1**.
6. Return to the product and deliberately Add to bag once again; quantity should become **2**.
7. Test quick view: default quantity **1**, one click adds **1**.
8. Rapidly double-click Add to bag; only one request should be accepted while the first is pending.
9. Sign out and try checkout; login/register must be required.
10. Sign in, complete a Razorpay Test Mode payment, and confirm the order is placed/paid.
11. Confirm the paid order appears under **Account → My orders**.
12. Confirm the paid order's cart is cleared.

## Important

Do not delete the existing database, products, accounts, media, or Razorpay `.env` values. This patch is designed to be applied on top of the current integrated project.
