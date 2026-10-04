# SUHAASA V15 — Frontend Approval Candidate

This version is intended for business-owner design approval before backend work begins.

## Final polish pass
- Removed placeholder `href="#"` footer links.
- Added usable footer help interactions for Contact, Shipping, Returns and FAQs.
- Added newsletter/story navigation in the footer.
- Added keyboard focus states for links, buttons, inputs and selects.
- Added Escape/backdrop closing for the cart drawer and footer information modal.
- Added dialog semantics and accessible labels to key overlays and quantity controls.
- Made product Quick View accessible on touch/mobile layouts.
- Added reduced-motion support for users who prefer less animation.
- Kept the textile/craft Our Story direction.

## Content intentionally left for the approved brand data
The business email, phone number, social handles, final shipping policy, return policy and FAQ answers are not invented. The UI is ready for those real details once supplied by the business.

## Validation note
A production build could not be completed in this environment because `npm install` timed out while resolving packages. The source was checked for placeholder footer links and the expected frontend sections/components remain present. Run `npm install` and `npm run build` locally before deployment.
