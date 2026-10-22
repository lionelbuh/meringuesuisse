/* ==========================================================================
   MERINGUE SUISSE — site settings. Edit this file to change prices, flavors,
   the Stripe link, contact details. No other code needs to change.
   ========================================================================== */
window.SITE = {
  // ---- Payment -------------------------------------------------------------
  // URL of your Stripe checkout worker (see STRIPE-SETUP.md), e.g.
  // "https://meringuesuisse-checkout.<your-account>.workers.dev".
  // While empty, the checkout button shows a friendly "payment link coming soon" note.
  checkoutEndpoint: "https://meringuesuisse-checkout.buhler-lionel.workers.dev",

  // SALES SWITCH. false = permit pending: no cart checkout or payment, the shop and cart
  // show a "join the waiting list" form instead. Set to true (and SALES_OPEN=true in the
  // Cloudflare Worker) once the Riverside County permit is received.
  salesOpen: false,

  // Label of the checkout button when sales are open.
  checkoutLabel: "Checkout",

  // ---- Forms ---------------------------------------------------------------
  // Optional: a Formspree (or similar) endpoint, e.g. "https://formspree.io/f/xxxxxxx".
  // If empty, forms open the visitor's email app addressed to contactEmail.
  formEndpoint: "https://formspree.io/f/mbgdzqke",
  contactEmail: "hello@meringuesuisse.com",
  instagramUrl: "",            // e.g. "https://instagram.com/yourhandle" — footer link appears when set

  // ---- Shipping ------------------------------------------------------------
  // Shipping is NOT included in the product price. Flat fee by number of boxes
  // in the cart. The first tier whose maxBoxes covers the cart applies;
  // maxBoxes: null means "and above". Keep in sync with stripe-checkout/worker.js.
  shippingTiers: [
    { maxBoxes: 2,    price: 9.90  },   // 1 to 2 boxes: small order
    { maxBoxes: 4,    price: 12.90 },   // 3 to 4 boxes: medium parcel
    { maxBoxes: 7,    price: 14.90 },   // 5 to 7 boxes: heavier parcel
    { maxBoxes: null, price: 0     }    // 8+ boxes: free shipping
  ],
  // Free local delivery (left at the front door) for these ZIP codes:
  // Temecula, Murrieta, Wildomar, French Valley. Keep in sync with stripe-checkout/worker.js.
  localDelivery: {
    label: "Free local delivery (Temecula area)",
    zips: ["92590", "92591", "92592", "92593", "92562", "92563", "92564", "92595", "92596"]
  },

  // ---- Products ------------------------------------------------------------
  currency: "USD",
  product: {
    name: "PETITES",
    description: "Nine delicate meringues, carefully arranged in our signature gift box.",
    // Add 18 / 27 boxes later by setting enabled: true (or adding a line).
    sizes: [
      { id: "box-9",  label: "Box of 9",  count: 9,  price: 14.90, enabled: true  },
      { id: "box-18", label: "Box of 18", count: 18, price: 0,     enabled: false },
      { id: "box-27", label: "Box of 27", count: 27, price: 0,     enabled: false }
    ],
    flavors: [
      { id: "classic",   name: "Classic",   enabled: true },
      { id: "coffee",    name: "Coffee",    enabled: true },
      { id: "chocolate", name: "Chocolate", enabled: true }
    ]
  }
};
