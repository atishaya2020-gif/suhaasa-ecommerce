# SUHAASA Frontend V4

Premium frontend prototype for the SUHAASA clothing and home-textiles storefront.

## What's included
- Clothing-first editorial hero
- Local bundled demo imagery (no Unsplash/external image dependency)
- 14 demo products across Kurtas, Bedsheets and Towels
- Shop filtering and sorting
- Product detail pages with gallery, size, quantity and accordions
- Frontend cart and wishlist interactions
- Search overlay, mobile menu and dusk theme toggle
- Framer Motion transitions and micro-interactions
- Responsive layout

## Run
```bash
npm install
npm run dev
```

## ngrok preview

This Vite config allows ngrok preview hostnames (`.ngrok-free.dev` and `.ngrok-free.app`) for local review.

Run:

```powershell
npm install
npm run dev
```

Then in a second terminal:

```powershell
ngrok http http://localhost:5173
```

Open the HTTPS forwarding URL printed by ngrok.
