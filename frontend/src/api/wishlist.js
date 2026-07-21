import { apiFetch } from "./client.js";

export function fetchWishlist() {
  return apiFetch("/api/wishlist/");
}

export function addWishlistItem(product) {
  return apiFetch("/api/wishlist/", { method: "POST", body: { product } });
}

export function removeWishlistItem(id) {
  return apiFetch(`/api/wishlist/${id}/`, { method: "DELETE" });
}
