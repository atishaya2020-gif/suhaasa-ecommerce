# SUHAASA Commerce Milestone 9 — Add-to-Bag Double-Click Protection

This is a patch for the existing integrated SUHAASA project.

## What this fixes

The previous Add-to-Bag lock only lasted while the API request was pending. On a very fast double-click, the first request could finish before the second click event was processed, allowing the second request to reach the backend and increase the existing cart line from 1 to 2.

This milestone keeps the same variant locked for **750ms after a successful Add-to-Bag response** as well as during the request. The result is:

- One click with quantity 1 → cart quantity 1.
- A rapid double-click with quantity 1 → cart quantity remains 1.
- A deliberate Add-to-Bag click after the short protection window → cart quantity becomes 2, as intended.
- Product-detail quantity remains 1 by default.
- Quick-view quantity remains 1 by default.
- Cart + / − remains the explicit way to change quantity.
- Failed Add-to-Bag requests unlock immediately so the customer can retry.

## Apply

Replace only:

```text
frontend/src/main.jsx
```

Do not replace the database, backend, products, accounts, media, or Razorpay configuration.

## Run

Frontend:

```powershell
cd C:\Users\OMEN\Desktop\suhaasa-build-integrated\frontend
npm run dev
```

## Regression test

1. Clear the existing cart first if it contains an old quantity of 2.
2. Open a fresh product detail page.
3. Confirm displayed quantity is **1**.
4. Double-click **Add to bag** quickly.
5. Open the cart: the item must show **quantity 1**.
6. Wait more than a second, then deliberately click **Add to bag** once again.
7. The same item should then show **quantity 2**.
8. Repeat with Quick View: default quantity **1**, rapid double-click still adds only **1**.
9. Test the cart `+` button separately; it should increase quantity to 2 normally.

## Important

The backend intentionally keeps additive semantics for separate Add-to-Bag actions. The frontend protection distinguishes a rapid accidental double-click from a later deliberate second Add-to-Bag action.
