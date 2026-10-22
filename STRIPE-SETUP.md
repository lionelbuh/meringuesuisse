# Stripe setup — Meringue Suisse

The site is hosted on GitHub Pages, which has no server. A plain Stripe Payment Link
can't receive the cart (flavors, quantities) or apply shipping by number of boxes,
so a small free **Cloudflare Worker** (`stripe-checkout/worker.js`) builds the Stripe
Checkout page from the cart, with these shipping fees:

| Boxes in cart | Shipping |
|---|---|
| 1 to 2 (small order) | $9.90 |
| 3 to 4 (medium parcel) | $12.90 |
| 5 to 7 (heavier parcel) | $14.90 |
| 8 or more | Free |

Prices and shipping are set inside the worker, so nobody can change them from the browser.

## 1. Create the Stripe account (about 15 minutes)
1. Sign up at <https://dashboard.stripe.com/register> with hello@meringuesuisse.com (or your own email).
2. Leave it in **Test mode** (toggle top right) while you set things up. Nothing is charged in test mode.
3. To accept real payments, click **Activate payments** and fill in:
   - Business type (sole proprietor or LLC), legal name, EIN or SSN, business address
   - Industry: *Food & beverage → Bakeries / Confectionery*
   - Website: `https://meringuesuisse.com` (Stripe checks that it shows prices, contact info, and
     Shipping/Returns, Privacy and Terms pages; they already exist, but fill in the yellow "to be added" notes first)
   - Bank account for payouts
   - Statement descriptor, for example `MERINGUESUISSE`
4. **Settings → Customer emails**: turn on *Successful payments* so customers get a receipt.
5. **Settings → Business → Public details**: add your support email and phone.

## 2. Get the secret key
**Developers → API keys** → copy the **Secret key** (`sk_test_...` in test mode).
Never put this key in the website files or on GitHub.

## 3. Deploy the worker (free, about 10 minutes)
1. Create a free account at <https://dash.cloudflare.com/sign-up>.
2. **Workers & Pages → Create → Create Worker** → name it `meringuesuisse-checkout` → **Deploy**.
3. **Edit code** → replace everything with the contents of `stripe-checkout/worker.js` → **Deploy**.
4. Worker → **Settings → Variables and Secrets → Add** → type *Secret*, name `STRIPE_SECRET_KEY`,
   value = your secret key → **Deploy**.
5. Copy the worker URL, for example `https://meringuesuisse-checkout.your-name.workers.dev`.

## 4. Connect the website
In `assets/config.js`, set:
```js
checkoutEndpoint: "https://meringuesuisse-checkout.your-name.workers.dev",
```
Commit. The cart button now opens Stripe Checkout.

The worker only accepts requests from `meringuesuisse.com`, so test on the live site, not by opening the files on your computer.

## 5. Test, then go live
1. On the live site, add boxes to the cart and click **Order on the Waiting List**.
2. Pay with test card `4242 4242 4242 4242`, any future date, any CVC, any ZIP.
3. Check the shipping line: 1–2 boxes = $9.90, 3–4 = $12.90, 5–7 = $14.90, 8+ = $0.00.
4. You land on the Thank You page and the cart is emptied. The order appears in Stripe → **Payments**,
   with flavors, quantities, shipping address and phone.
5. Go live: activate the account (step 1.3), copy the **live** secret key (`sk_live_...`) and replace
   `STRIPE_SECRET_KEY` in the worker. No change is needed on the website.

## Changing prices or shipping later
Change **both** `assets/config.js` (what the cart shows) and the top of `stripe-checkout/worker.js`
(what Stripe charges), then re-deploy the worker (Edit code → paste → Deploy).
Worker prices are in cents: `1490` = $14.90.

## Good to know
- Stripe Checkout restricts shipping by country, not by state. It is set to the US only.
  If someone orders from outside California, refund them from the Stripe dashboard.
- Stripe fees are about 2.9% + $0.30 per card payment (check Stripe's pricing page).
- California sales tax: plain bakery food is generally exempt, but confirm with the CDTFA or your
  accountant. If needed, Stripe Tax can be turned on later.

## Free-box promo codes (loyalty)
Each code **adds one free box** (flavor chosen by the customer) to an order of at least one paid box.
Shipping is charged on the paid boxes only. A code works **once** and has **no expiry**.
Technically the Worker adds the extra box to the Stripe order and the $14.90 coupon (limited to the
PETITES products, never shipping) cancels exactly that box. Stripe stores the codes, applies the discount and blocks
reuse; the cart has a "Have a free-box code?" field and the Worker checks codes server-side.

### One-time setup
1. Re-deploy the Worker with the latest `stripe-checkout/worker.js` (Edit code → paste → Deploy).
2. Worker → **Settings → Variables and Secrets → Add** → type *Secret*, name `ADMIN_TOKEN`,
   value = a long random password (at least 16 characters, e.g. from a password manager) → Deploy.
3. Open the Worker URL: it should show `"promoAdmin":"enabled"`.

The first order or the first batch creates, in Stripe, three products (`ms_petites_classic`,
`ms_petites_coffee`, `ms_petites_chocolate`) and the coupon **Free box (PETITES)**
(`ms-free-box`). Don't delete or rename their IDs.

### Generate and export codes
1. Open `https://meringuesuisse.com/promo-admin` (private page, not linked anywhere).
2. Enter the `ADMIN_TOKEN`, the number of codes (e.g. 100) and a batch label (e.g. `2026-11`).
3. **Generate & download CSV** → `free-box-codes-<batch>.csv` (`code, status, times_redeemed, batch, created`).
   Keep this file private: each code is worth a free box.
4. **Download status CSV** at any time to see which codes are available, used or disabled.
5. To disable a code: Stripe → **Product catalog → Coupons → Free box (PETITES) → Promotion codes** → the code → Archive.

The page shows whether the Worker is in TEST or LIVE mode. Test-mode codes don't work in live mode:
generate the real batch after switching the Worker to the `sk_live_` key.

### Test before using real codes (Stripe test mode, card 4242 4242 4242 4242)
- 1 box + code → you receive **2 boxes** and pay **$14.90 + $9.90 shipping**.
- 2 boxes + code → you receive **3 boxes** and pay **$29.80 + $9.90 shipping** (shipping on the 2 paid boxes).
- The same code again after a paid order → refused.
- A made-up code → refused. An order without a code → unchanged.
- **Two tabs, same unused code, open both payment pages and pay both** → only one should go through.
  If both succeed, tell Claude: a small lock can be added in the Worker (free).
- Check the status CSV: the codes you used show `used`.

## Sales switch (permit pending)
While the Riverside County permit is pending, sales are **closed**:
- `assets/config.js` → `salesOpen: false`: the shop and cart show "Permit pending" and a
  "Join the waiting list" email form (sent through Formspree, with the flavor they were interested in).
- Worker: without the variable `SALES_OPEN = true`, it refuses to create any payment page.

To open sales once the permit arrives:
1. Ask Claude to set `salesOpen: true` (or edit `assets/config.js` yourself and bump the `?v=` numbers).
2. Cloudflare → Worker → **Settings → Variables and Secrets → Add** → type *Text*, name `SALES_OPEN`,
   value `true` → **Deploy**. The Worker URL then shows `"sales":"open"`.
