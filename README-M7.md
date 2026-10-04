# SUHAASA Commerce Milestone 7 — Add-to-Bag Quantity Fix

Patch for the existing integrated SUHAASA project. Do **not** replace the whole project or database.

## Apply

1. Back up your current project.
2. Replace only:
   - `backend/commerce/views.py`
   - `frontend/src/main.jsx`
3. No database migration is required.
4. Restart Django and Vite.

## What changed

- Product detail and quick-view quantities remain initialized to **1**.
- Add-to-bag now has a client-side in-flight lock keyed by variant/size. A double-click, rapid click, or overlapping React event cannot submit the same Add-to-bag action twice while the first request is pending.
- Backend keeps explicit quantity semantics: a newly created cart line starts at the requested quantity; subsequent intentional Add-to-bag actions add the requested quantity.
- Cart `+/-` remains the authoritative way to change an existing cart line quantity.

## Required regression test

1. Clear the existing test cart first (through the UI, not by deleting database rows blindly).
2. Open a product detail page.
3. Confirm displayed quantity is `1`.
4. Click **Add to bag once**.
5. Open the cart: that variant must show **quantity 1**.
6. Refresh: it must still show **quantity 1**.
7. Return to the same product and intentionally click Add to bag once again: quantity should become **2** because this is a second deliberate Add-to-bag action.
8. Repeat with quick view: default quantity must be **1** and one deliberate click must add exactly one.
9. Rapidly double-click Add to bag: only one request should be accepted while the first is pending.
10. Test cart `+/-` controls separately.

## Important

The persistent cart from earlier tests may already contain quantity 2. That old database state is not evidence of a new duplicate submission. Clear it before the fresh regression test.
