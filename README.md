# MeringueSuisse.com — static site

Plain HTML/CSS/JS. No build step, no dependencies. Works on GitHub Pages.

## Publish on GitHub Pages
1. Create a repo and push the contents of this folder to the `main` branch.
2. Repo **Settings → Pages → Deploy from a branch → `main` / root**.
3. Custom domain: add `meringuesuisse.com` under Pages → Custom domain (GitHub creates the `CNAME` file), then point your DNS to GitHub Pages. HTTPS is automatic.

## Payments (Stripe)
Follow **[STRIPE-SETUP.md](STRIPE-SETUP.md)**: create the Stripe account, deploy the small checkout worker
(`stripe-checkout/worker.js`, free on Cloudflare), then paste its URL into `checkoutEndpoint` in `assets/config.js`.
Until then, the cart's **"Order on the Waiting List"** button shows a "payment link coming soon" note.

## Free-box promo codes
One-use codes for a free box (shipping still paid), managed in Stripe. Generate and export them at `/promo-admin`. See **[STRIPE-SETUP.md](STRIPE-SETUP.md#free-box-promo-codes-loyalty)**.

## Shipping
Flat fee by number of boxes, set in `shippingTiers` in `assets/config.js` (and in `stripe-checkout/worker.js`):
$9.90 for 1–2 boxes, $12.90 for 3–4, $14.90 for 5–7, free for 8 or more.

## Change prices, flavors, contact email, shipping
All in `assets/config.js`: prices, flavors, box sizes (18 and 27 are pre-built, just set a price and `enabled: true`), `contactEmail`, `instagramUrl`, `shippingTiers`. Prices and shipping must also be updated in `stripe-checkout/worker.js`.

## Replace photos (no code change)
Overwrite the file in `images/` using the same file name:

| File | Used for |
|---|---|
| `hero.jpg` | Home page hero, shop gallery (open box, 9 meringues) |
| `box-open.jpg` | Shop main photo, home gift row (open box with card) |
| `gift-set.jpg` | Home "Small delights" section (tied box) |
| `box-closed.jpg` | Tied box with tag (home gift row, shop gallery) |
| `story-card.jpg` | Story card (home gift row) |
| `closeup.jpg` | Meringue close-up (shop gallery) |
| `classic.jpg`, `coffee.jpg`, `chocolate.jpg` | Flavor cards and cart |
| `switzerland.jpg` | Swiss spirit band and Our Story page |
| `share.jpg` | Link previews (1200 x 630, made from `gift-set.jpg`) |

Tip: JPEG, about 1200–1600 px wide, under 300 KB.

## Forms (contact + newsletter)
GitHub Pages has no server. By default the forms open the visitor's email app addressed to `hello@meringuesuisse.com`.
For real submissions, create a free Formspree form and paste its URL into `formEndpoint` in `config.js`.

## Still to fill in (yellow "to be added" notes on the site)
Legal business name/address, permit details, ingredients, allergens, net weight, delivery times, shelf life, final Privacy/Terms review.

## Browser cache
Pages load `assets/style.css`, `config.js` and `site.js` with a `?v=YYYYMMDD` suffix. After changing one of
those files, bump the number in every `.html` page so visitors get the new version immediately
(otherwise browsers may keep the old file for up to 10 minutes).
