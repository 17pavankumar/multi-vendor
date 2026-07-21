import { apiFetch } from "./client.js";

function toQueryString(params) {
  const cleaned = Object.fromEntries(
    Object.entries(params).filter(([, value]) => value !== undefined && value !== null && value !== ""),
  );
  const query = new URLSearchParams(cleaned).toString();
  return query ? `?${query}` : "";
}

/** @param {{search?: string, category?: string, min_price?: string, max_price?: string, page?: number}} [params] */
export function fetchProducts(params = {}) {
  return apiFetch(`/api/products/${toQueryString(params)}`, { auth: false });
}

export function fetchProduct(slug) {
  return apiFetch(`/api/products/${slug}/`, { auth: false });
}
