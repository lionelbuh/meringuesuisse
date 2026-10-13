/* ==========================================================================
   MERINGUE SUISSE — site settings. Edit this file to change prices, flavors,
   the Stripe link, contact details. No other code needs to change.
   ========================================================================== */
window.SITE = {
  // ---- Payment -------------------------------------------------------------
  // Paste your Stripe Payment Link here (https://buy.stripe.com/...) when ready.
  // While empty, the checkout button shows a friendly "payment link coming soon" note.
  stripeLink: "",

  // Label of the checkout button (advance orders only, before market launch).
  checkoutLabel: "Order on the Waiting List",

  // ---- Forms ---------------------------------------------------------------
  // Optional: a Formspree (or similar) endpoint, e.g. "https://formspree.io/f/xxxxxxx".
  // If empty, forms open the visitor's email app addressed to contactEmail.
  formEndpoint: "",
  contactEmail: "hello@meringuesuisse.com",
  instagramUrl: "",            // e.g. "https://instagram.com/yourhandle" — footer link appears when set

  // ---- Shipping ------------------------------------------------------------
  // Shipping is NOT included in the product price. Leave null until validated.
  // Example later: shippingFlat: 8.00
  shippingFlat: null,

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
