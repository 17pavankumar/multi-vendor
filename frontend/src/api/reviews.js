import { apiFetch } from "./client.js";

export function fetchProductReviews(productId) {
  return apiFetch(`/api/reviews/product/${productId}/`, { auth: false });
}
