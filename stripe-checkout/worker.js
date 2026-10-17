/* ==========================================================================
   MERINGUE SUISSE — Stripe checkout worker (Cloudflare Workers, free plan).
   The website (GitHub Pages) has no server, so this tiny worker creates the
   Stripe Checkout page from the cart. Prices and shipping are set HERE, not
   trusted from the browser. See STRIPE-SETUP.md for deployment.

   Required secret (Worker → Settings → Variables and Secrets):
     STRIPE_SECRET_KEY   sk_test_... while testing, sk_live_... when live
   ========================================================================== */

const SITE = "https://meringuesuisse.com";
const ALLOWED_ORIGINS = [SITE, "https://www.meringuesuisse.com"];
const CURRENCY = "usd";
const PRODUCT = "PETITES";

// Prices in cents. Keep in sync with assets/config.js.
const SIZES = {
  "box-9": { label: "Box of 9", price: 1490 }
  // "box-18": { label: "Box of 18", price: 0 },
};
const FLAVORS = { classic: "Classic", coffee: "Coffee", chocolate: "Chocolate" };

// Flat shipping by number of boxes. maxBoxes: null = "and above".
const SHIPPING_TIERS = [
  { maxBoxes: 2, price: 990, name: "Small order shipping (1–2 boxes)" },
  { maxBoxes: 4, price: 1290, name: "Medium parcel shipping (3–4 boxes)" },
  { maxBoxes: 7, price: 1490, name: "Heavier parcel shipping (5–7 boxes)" },
  { maxBoxes: null, price: 0, name: "Free shipping (8+ boxes)" }
];

const MAX_QTY_PER_LINE = 20;
const MAX_BOXES = 60;

export default {
  async fetch(request, env) {
    const origin = request.headers.get("Origin") || "";
    const cors = {
      "Access-Control-Allow-Origin": ALLOWED_ORIGINS.includes(origin) ? origin : SITE,
      "Access-Control-Allow-Methods": "POST, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type",
      "Vary": "Origin"
    };
    const json = (body, status = 200) =>
      new Response(JSON.stringify(body), { status, headers: { ...cors, "Content-Type": "application/json" } });

    if (request.method === "OPTIONS") return new Response(null, { status: 204, headers: cors });
    // Opening the worker URL in a browser shows a quick health check.
    if (request.method === "GET") {
      const key = env.STRIPE_SECRET_KEY || "";
      return json({
        worker: "ok",
        stripeKey: !key ? "MISSING - add the STRIPE_SECRET_KEY secret"
          : key.startsWith("sk_test_") ? "test key ok"
          : key.startsWith("sk_live_") ? "live key ok"
          : key.startsWith("rk_") ? "restricted key - use the Secret key (sk_...) instead"
          : "WRONG KEY - it must start with sk_test_ or sk_live_ (not pk_)"
      });
    }
    if (request.method !== "POST") return json({ error: "Method not allowed" }, 405);
    if (!ALLOWED_ORIGINS.includes(origin)) return json({ error: "Forbidden origin: " + origin }, 403);
    if (!env.STRIPE_SECRET_KEY) return json({ error: "STRIPE_SECRET_KEY secret is missing" }, 500);

    let items;
    try { items = (await request.json()).items; } catch { return json({ error: "Invalid request" }, 400); }
    if (!Array.isArray(items) || !items.length) return json({ error: "Cart is empty" }, 400);

    const params = new URLSearchParams();
    let boxes = 0, i = 0;
    for (const it of items) {
      const size = SIZES[it && it.size], flavor = FLAVORS[it && it.flavor], qty = Number(it && it.qty);
      if (!size || !flavor || !Number.isInteger(qty) || qty < 1 || qty > MAX_QTY_PER_LINE)
        return json({ error: "Invalid item in cart" }, 400);
      boxes += qty;
      params.append(`line_items[${i}][quantity]`, qty);
      params.append(`line_items[${i}][price_data][currency]`, CURRENCY);
      params.append(`line_items[${i}][price_data][unit_amount]`, size.price);
      params.append(`line_items[${i}][price_data][product_data][name]`, `${PRODUCT} — ${flavor} (${size.label})`);
      i++;
    }
    if (boxes > MAX_BOXES) return json({ error: "Order too large, please contact us" }, 400);

    const tier = SHIPPING_TIERS.find(t => t.maxBoxes == null || boxes <= t.maxBoxes);
    params.append("mode", "payment");
    params.append("success_url", `${SITE}/thank-you?session_id={CHECKOUT_SESSION_ID}`);
    params.append("cancel_url", `${SITE}/cart`);
    params.append("shipping_address_collection[allowed_countries][0]", "US");
    params.append("shipping_options[0][shipping_rate_data][type]", "fixed_amount");
    params.append("shipping_options[0][shipping_rate_data][display_name]", tier.name);
    params.append("shipping_options[0][shipping_rate_data][fixed_amount][amount]", tier.price);
    params.append("shipping_options[0][shipping_rate_data][fixed_amount][currency]", CURRENCY);
    params.append("phone_number_collection[enabled]", "true");
    params.append("metadata[boxes]", boxes);

    const res = await fetch("https://api.stripe.com/v1/checkout/sessions", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${env.STRIPE_SECRET_KEY}`,
        "Content-Type": "application/x-www-form-urlencoded"
      },
      body: params
    });
    const session = await res.json();
    if (!res.ok) {
      console.error("Stripe error", session && session.error);
      return json({ error: "Stripe: " + ((session && session.error && session.error.message) || res.status) }, 502);
    }
    return json({ url: session.url });
  }
};
