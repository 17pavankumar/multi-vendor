import { apiFetch } from "./client.js";

export function fetchCart() {
  return apiFetch("/api/cart/");
}

export function addCartItem({ product, quantity = 1 }) {
  return apiFetch("/api/cart/items/", { method: "POST", body: { product, quantity } });
}

export function updateCartItem(id, { quantity }) {
  return apiFetch(`/api/cart/items/${id}/`, { method: "PATCH", body: { quantity } });
}

export function removeCartItem(id) {
  return apiFetch(`/api/cart/items/${id}/`, { method: "DELETE" });
}

export function clearCart() {
  return apiFetch("/api/cart/clear/", { method: "DELETE" });
}
