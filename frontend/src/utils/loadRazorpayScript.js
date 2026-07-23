const RAZORPAY_SCRIPT_URL = "https://checkout.razorpay.com/v1/checkout.js";

let loadPromise = null;

/** Loads Razorpay's checkout widget script once and caches the
 * in-flight promise, so navigating to checkout more than once in a
 * session doesn't re-inject the <script> tag. Resolves to false
 * (rather than rejecting) on failure, since a network hiccup loading a
 * third-party script shouldn't throw — the caller decides what a
 * failed load means for the user. */
export function loadRazorpayScript() {
  if (window.Razorpay) return Promise.resolve(true);
  if (loadPromise) return loadPromise;

  loadPromise = new Promise((resolve) => {
    const script = document.createElement("script");
    script.src = RAZORPAY_SCRIPT_URL;
    script.onload = () => resolve(true);
    script.onerror = () => resolve(false);
    document.body.appendChild(script);
  });
  return loadPromise;
}
