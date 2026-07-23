import { apiFetch } from "./client.js";

export function verifyPayment({ razorpayOrderId, razorpayPaymentId, razorpaySignature }) {
  return apiFetch("/api/payments/verify/", {
    method: "POST",
    body: {
      razorpay_order_id: razorpayOrderId,
      razorpay_payment_id: razorpayPaymentId,
      razorpay_signature: razorpaySignature,
    },
  });
}
