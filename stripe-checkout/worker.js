/* ==========================================================================
   MERINGUE SUISSE — Stripe checkout worker (Cloudflare Workers, free plan).
   The website (GitHub Pages) has no server, so this tiny worker creates the
   Stripe Checkout page from the cart. Prices and shipping are set HERE, not
   trusted from the browser. See STRIPE-SETUP.md for deployment.

   Secrets (Worker → Settings → Variables and Secrets):
     STRIPE_SECRET_KEY   sk_test_... while testing, sk_live_... when live
     ADMIN_TOKEN         long random password for the promo-code admin page
                         (optional: without it, the admin actions are disabled)
   Variable (plain text):
     SALES_OPEN          "true" to accept orders and payments. Missing or anything else = closed
                         (permit pending): the payment page is never created.

   Requests (POST, JSON body):
     { items, promo? }                       → { url }   create the payment page
     { action: "check", code }               → { ok, code, amount, label } | { ok:false, error }
     { action: "admin-generate", count, batch }   (Authorization: Bearer ADMIN_TOKEN) → { codes:[...] }
     { action: "admin-status" }                   (Authorization: Bearer ADMIN_TOKEN) → { codes:[...] }
   ========================================================================== */

const SITE = "https://meringuesuisse.com";
const ALLOWED_ORIGINS = [SITE, "https://www.meringuesuisse.com"];
const CURRENCY = "usd";
const PRODUCT = "PETITES";
// Pin the Stripe API version so request/response shapes never change under us.
const STRIPE_VERSION = "2024-06-20";

// Prices in cents. Keep in sync with assets/config.js.
const SIZES = {
  "box-9": { label: "Box of 9", price: 1490 }
  // "box-18": { label: "Box of 18", price: 0 },
};
const FLAVORS = { classic: "Classic", coffee: "Coffee", chocolate: "Chocolate" };
// Fixed Stripe product IDs (created automatically) so the free-box coupon can target them.
const PRODUCT_ID = flavor => `ms_petites_${flavor}`;

// Flat shipping by number of boxes. maxBoxes: null = "and above".
const SHIPPING_TIERS = [
  { maxBoxes: 2, price: 990, name: "Small order shipping (1–2 boxes)" },
  { maxBoxes: 4, price: 1290, name: "Medium parcel shipping (3–4 boxes)" },
  { maxBoxes: 7, price: 1490, name: "Heavier parcel shipping (5–7 boxes)" },
  { maxBoxes: null, price: 0, name: "Free shipping (8+ boxes)" }
];

// Free-box loyalty coupon: a fixed $14.90 off, limited to the PETITES products,
// so it frees exactly one box and never touches shipping.
const FREE_BOX = { couponId: "ms-free-box", name: "Free box (PETITES)", amount: 1490, label: "Free box" };
const CODE_PREFIX = "PETITES-";
const CODE_ALPHABET = "ABCDEFGHJKMNPQRSTUVWXYZ23456789"; // no 0/O, 1/I/L
const CODE_LENGTH = 6;
const MAX_GENERATE_PER_CALL = 20; // stays under the Workers free-plan subrequest limit

// Free local delivery (front door) — Temecula + ~10 miles. Keep in sync with assets/config.js.
const LOCAL_ZIPS = ["92590", "92591", "92592", "92593", "92562", "92563", "92564", "92595", "92596"];
// Delivery estimates shown on the Stripe page: 3–5 business days to make + USPS Ground Advantage 2–5.
const ESTIMATE_SHIP = { min: 5, max: 10 };
const ESTIMATE_LOCAL = { min: 3, max: 5 };

const MAX_QTY_PER_LINE = 20;
const MAX_BOXES = 60;

export default {
  async fetch(request, env) {
    const origin = request.headers.get("Origin") || "";
    const cors = {
      "Access-Control-Allow-Origin": ALLOWED_ORIGINS.includes(origin) ? origin : SITE,
      "Access-Control-Allow-Methods": "POST, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type, Authorization",
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
          : "WRONG KEY - it must start with sk_test_ or sk_live_ (not pk_)",
        sales: env.SALES_OPEN === "true" ? "open" : "closed (add the variable SALES_OPEN = true to accept orders)",
        promoAdmin: !String(env.ADMIN_TOKEN || "").trim() ? "disabled (add the ADMIN_TOKEN secret to enable)"
          : String(env.ADMIN_TOKEN).trim().length < 16 ? "disabled: ADMIN_TOKEN is shorter than 16 characters"
          : "enabled"
      });
    }
    if (request.method !== "POST") return json({ error: "Method not allowed" }, 405);
    if (!ALLOWED_ORIGINS.includes(origin)) return json({ error: "Forbidden origin: " + origin }, 403);
    if (!env.STRIPE_SECRET_KEY) return json({ error: "STRIPE_SECRET_KEY secret is missing" }, 500);

    let body;
    try { body = await request.json(); } catch { return json({ error: "Invalid request" }, 400); }
    const stripe = stripeClient(env.STRIPE_SECRET_KEY);

    try {
      if (body.action === "check") {
        const promo = await findFreeBoxCode(stripe, body.code);
        if (!promo) return json({ ok: false, error: "This code is not valid or has already been used." });
        return json({ ok: true, code: promo.code, amount: FREE_BOX.amount, label: FREE_BOX.label });
      }
      if (body.action === "admin-generate" || body.action === "admin-status") {
        const why = adminProblem(request, env);
        if (why) return json({ error: why }, 401);
        if (body.action === "admin-status") return json({ codes: await listCodes(stripe) });
        const count = Math.floor(Number(body.count));
        if (!(count >= 1 && count <= MAX_GENERATE_PER_CALL)) return json({ error: `count must be 1-${MAX_GENERATE_PER_CALL}` }, 400);
        const batch = String(body.batch || "").replace(/[^\w.-]/g, "").slice(0, 40) || new Date().toISOString().slice(0, 10);
        await ensureCatalog(stripe);
        return json({ codes: await generateCodes(stripe, count, batch) });
      }
      if (env.SALES_OPEN !== "true") return json({ error: "Ordering is not open yet: our permit is pending." }, 403);
      return await checkout(stripe, body, json);
    } catch (e) {
      console.error("Worker error", e && e.message);
      return json({ error: "Stripe: " + ((e && e.message) || "error") }, 502);
    }
  }
};

async function checkout(stripe, body, json) {
  const items = body.items;
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
    params.append(`line_items[${i}][price_data][product]`, PRODUCT_ID(it.flavor));
    i++;
  }
  if (boxes > MAX_BOXES) return json({ error: "Order too large, please contact us" }, 400);

  let tier = SHIPPING_TIERS.find(t => t.maxBoxes == null || boxes <= t.maxBoxes);
  let estimate = ESTIMATE_SHIP, shipName = tier.name + " — USPS Ground";
  const local = body.delivery && body.delivery.method === "local";
  if (local) {
    const zip = String(body.delivery.zip || "").trim().slice(0, 5);
    if (!LOCAL_ZIPS.includes(zip))
      return json({ error: "Free local delivery is only available in the Temecula area. Please choose shipping.", deliveryInvalid: true }, 400);
    tier = { price: 0 }; estimate = ESTIMATE_LOCAL; shipName = `Free local delivery — Temecula area (${zip})`;
    params.append("metadata[delivery]", "local");
    params.append("metadata[local_zip]", zip);
    params.append("custom_text[shipping_address][message]",
      `Free local delivery: please enter your address in ZIP ${zip}. We leave the box at your front door.`);
  }
  params.append("mode", "payment");
  params.append("success_url", `${SITE}/thank-you?session_id={CHECKOUT_SESSION_ID}`);
  params.append("cancel_url", `${SITE}/cart`);
  params.append("shipping_address_collection[allowed_countries][0]", "US");
  params.append("shipping_options[0][shipping_rate_data][type]", "fixed_amount");
  params.append("shipping_options[0][shipping_rate_data][display_name]", shipName);
  params.append("shipping_options[0][shipping_rate_data][delivery_estimate][minimum][unit]", "business_day");
  params.append("shipping_options[0][shipping_rate_data][delivery_estimate][minimum][value]", estimate.min);
  params.append("shipping_options[0][shipping_rate_data][delivery_estimate][maximum][unit]", "business_day");
  params.append("shipping_options[0][shipping_rate_data][delivery_estimate][maximum][value]", estimate.max);
  params.append("shipping_options[0][shipping_rate_data][fixed_amount][amount]", tier.price);
  params.append("shipping_options[0][shipping_rate_data][fixed_amount][currency]", CURRENCY);
  params.append("phone_number_collection[enabled]", "true");
  params.append("metadata[boxes]", boxes);

  if (body.promo) {
    // Validate server-side; Stripe checks the code again when the payment completes.
    const promo = await findFreeBoxCode(stripe, body.promo);
    if (!promo) return json({ error: "This code is not valid or has already been used.", promoInvalid: true }, 400);
    // The code ADDS one box of the customer's chosen flavor; the $14.90 coupon cancels exactly that box.
    // Shipping was already set from the paid boxes above, so the free box never raises it.
    const free = FLAVORS[body.freeFlavor] ? body.freeFlavor : "classic";
    params.append(`line_items[${i}][quantity]`, 1);
    params.append(`line_items[${i}][price_data][currency]`, CURRENCY);
    params.append(`line_items[${i}][price_data][unit_amount]`, SIZES["box-9"].price);
    params.append(`line_items[${i}][price_data][product]`, PRODUCT_ID(free));
    i++;
    params.append("metadata[free_box]", FLAVORS[free]);
    params.append("discounts[0][promotion_code]", promo.id);
    params.append("metadata[promo_code]", promo.code);
    // Short-lived page keeps the window for parallel use of one code small (min allowed is 30 min).
    params.append("expires_at", Math.floor(Date.now() / 1000) + 45 * 60);
  }

  let session;
  try {
    session = await stripe("POST", "/v1/checkout/sessions", params);
  } catch (e) {
    if (e.code !== "resource_missing") throw e;
    await ensureCatalog(stripe); // first order ever: create the products, then retry once
    session = await stripe("POST", "/v1/checkout/sessions", params);
  }
  return json({ url: session.url });
}

// ---- Stripe helpers ---------------------------------------------------------

function stripeClient(key) {
  return async function (method, path, params) {
    const res = await fetch("https://api.stripe.com" + path + (method === "GET" && params ? "?" + params : ""), {
      method,
      headers: {
        Authorization: `Bearer ${key}`,
        "Stripe-Version": STRIPE_VERSION,
        "Content-Type": "application/x-www-form-urlencoded"
      },
      body: method === "GET" ? undefined : params
    });
    const data = await res.json();
    if (!res.ok) {
      const err = new Error((data && data.error && data.error.message) || "HTTP " + res.status);
      err.code = data && data.error && data.error.code;
      err.status = res.status;
      throw err;
    }
    return data;
  };
}

function normalizeCode(code) {
  return String(code || "").trim().toUpperCase().replace(/\s+/g, "");
}

async function findFreeBoxCode(stripe, raw) {
  const code = normalizeCode(raw);
  if (!/^[A-Z0-9-]{4,40}$/.test(code)) return null;
  const q = new URLSearchParams({ code, active: "true", limit: "1" });
  const list = await stripe("GET", "/v1/promotion_codes", q);
  const p = list.data && list.data[0];
  if (!p || !p.active) return null;
  const couponId = typeof p.coupon === "string" ? p.coupon : p.coupon && p.coupon.id;
  if (couponId !== FREE_BOX.couponId) return null;
  if (p.max_redemptions != null && p.times_redeemed >= p.max_redemptions) return null;
  if (p.expires_at && p.expires_at * 1000 < Date.now()) return null;
  return p;
}

async function ensureCatalog(stripe) {
  try {
    await stripe("GET", "/v1/coupons/" + FREE_BOX.couponId);
    return; // coupon exists, so the products were created with it
  } catch (e) {
    if (e.code !== "resource_missing") throw e;
  }
  for (const [flavor, name] of Object.entries(FLAVORS)) {
    try {
      await stripe("POST", "/v1/products", new URLSearchParams({
        id: PRODUCT_ID(flavor),
        name: `${PRODUCT} — ${name} (Box of 9)`,
        "metadata[flavor]": flavor
      }));
    } catch (e) {
      if (e.code !== "resource_already_exists") throw e;
    }
  }
  const c = new URLSearchParams({
    id: FREE_BOX.couponId, name: FREE_BOX.name, amount_off: String(FREE_BOX.amount),
    currency: CURRENCY, duration: "once"
  });
  Object.keys(FLAVORS).forEach((f, i) => c.append(`applies_to[products][${i}]`, PRODUCT_ID(f)));
  try {
    await stripe("POST", "/v1/coupons", c);
  } catch (e) {
    if (e.code !== "resource_already_exists") throw e;
  }
}

function randomCode() {
  const out = [];
  const buf = new Uint8Array(32);
  const limit = 256 - (256 % CODE_ALPHABET.length); // rejection sampling: no bias
  while (out.length < CODE_LENGTH) {
    crypto.getRandomValues(buf);
    for (const b of buf) {
      if (b < limit) out.push(CODE_ALPHABET[b % CODE_ALPHABET.length]);
      if (out.length === CODE_LENGTH) break;
    }
  }
  return CODE_PREFIX + out.join("");
}

async function generateCodes(stripe, count, batch) {
  const codes = [];
  let attempts = 0;
  while (codes.length < count && attempts < count + 5) {
    attempts++;
    const code = randomCode();
    try {
      const p = await stripe("POST", "/v1/promotion_codes", new URLSearchParams({
        coupon: FREE_BOX.couponId, code, max_redemptions: "1", "metadata[batch]": batch
      }));
      codes.push(row(p));
    } catch (e) {
      if (e.status !== 400 || !/already exists|in use|duplicate/i.test(e.message)) throw e; // retry only on a code collision
    }
  }
  return codes;
}

async function listCodes(stripe) {
  const all = [];
  let after = null;
  for (let page = 0; page < 40; page++) { // up to 4,000 codes
    const q = new URLSearchParams({ coupon: FREE_BOX.couponId, limit: "100" });
    if (after) q.set("starting_after", after);
    const list = await stripe("GET", "/v1/promotion_codes", q);
    list.data.forEach(p => all.push(row(p)));
    if (!list.has_more || !list.data.length) break;
    after = list.data[list.data.length - 1].id;
  }
  return all;
}

function row(p) {
  const used = p.max_redemptions != null && p.times_redeemed >= p.max_redemptions;
  return {
    code: p.code,
    status: used ? "used" : p.active ? "available" : "disabled",
    times_redeemed: p.times_redeemed,
    batch: (p.metadata && p.metadata.batch) || "",
    created: new Date(p.created * 1000).toISOString().slice(0, 10)
  };
}

// Returns null when the request carries the right ADMIN_TOKEN, otherwise a message saying why not.
function adminProblem(request, env) {
  const token = String(env.ADMIN_TOKEN || "").trim();
  if (!token) return "ADMIN_TOKEN secret is missing in the Worker (Settings → Variables and Secrets), then Deploy.";
  if (token.length < 16) return "ADMIN_TOKEN in the Worker is too short: use at least 16 characters.";
  const got = (request.headers.get("Authorization") || "").replace(/^Bearer\s+/i, "").trim();
  if (!got) return "Enter the admin token.";
  let diff = got.length ^ token.length;
  for (let i = 0; i < token.length; i++) diff |= token.charCodeAt(i) ^ (got.charCodeAt(i) || 0);
  return diff === 0 ? null : "Wrong admin token (it must match the ADMIN_TOKEN secret exactly, capitals included).";
}
