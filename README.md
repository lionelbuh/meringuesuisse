# MeringueSuisse.com — static site

Plain HTML/CSS/JS. No build step, no dependencies. Works on GitHub Pages.

## Publish on GitHub Pages
1. Create a repo and push the contents of this folder to the `main` branch.
2. Repo **Settings → Pages → Deploy from a branch → `main` / root**.
3. Custom domain: add `meringuesuisse.com` under Pages → Custom domain (GitHub creates the `CNAME` file), then point your DNS to GitHub Pages. HTTPS is automatic.

## Add your Stripe link
Open `assets/config.js` and paste your Payment Link into `stripeLink`. Until then, the cart's
**"Order on the Waiting List"** button shows a "payment link coming soon" note.
Note: a Stripe Payment Link is a fixed product/price, so create one link per flavor/size (or enable adjustable quantity in Stripe).
If you want one link per flavor later, ask and I'll wire the flavors to separate links.

## Change prices, flavors, contact email, shipping
All in `assets/config.js`: prices, flavors, box sizes (18 and 27 are pre-built, just set a price and `enabled: true`), `contactEmail`, `instagramUrl`, `shippingFlat`.

## Replace photos (no code change)
Overwrite the file in `images/` using the same file name:

| File | Used for |
|---|---|
| `hero.jpg` | Home page hero (open box with 9 meringues) |
| `box-open.jpg` | Product section, shop gallery, gift section |
| `box-closed.jpg` | Closed box / packaging |
| `closeup.jpg`, `texture.jpg` | Close-ups (shop gallery) |
| `classic.jpg`, `coffee.jpg`, `chocolate.jpg` | Flavor cards and cart |
| `gift-card.jpg` | Box and story card |
| `switzerland.jpg` | Swiss spirit band and Our Story page |

Tip: JPEG, about 1200–1600 px wide, under 300 KB.

## Forms (contact + newsletter)
GitHub Pages has no server. By default the forms open the visitor's email app addressed to `hello@meringuesuisse.com`.
For real submissions, create a free Formspree form and paste its URL into `formEndpoint` in `config.js`.

## Still to fill in (yellow "to be added" notes on the site)
Legal business name/address, permit details, ingredients, allergens, net weight, delivery times, shelf life, final Privacy/Terms review.
