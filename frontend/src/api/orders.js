import { apiFetch } from "./client.js";

export function checkout({ shippingAddressId, billingAddressId, couponCode }) {
  return apiFetch("/api/orders/checkout/", {
    method: "POST",
    body: {
      shipping_address_id: shippingAddressId,
      billing_address_id: billingAddressId,
      coupon_code: couponCode || undefined,
    },
  });
}

export function fetchOrders() {
  return apiFetch("/api/orders/");
}

export function fetchOrder(id) {
  return apiFetch(`/api/orders/${id}/`);
}
