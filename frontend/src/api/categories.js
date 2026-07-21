import { apiFetch } from "./client.js";

/** @param {{parent?: string}} [params] - pass parent: "null" for top-level categories only */
export function fetchCategories(params = {}) {
  const query = new URLSearchParams(params).toString();
  return apiFetch(`/api/categories/${query ? `?${query}` : ""}`, { auth: false });
}
