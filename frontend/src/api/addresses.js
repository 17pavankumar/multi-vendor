import { apiFetch } from "./client.js";

export function fetchAddresses() {
  return apiFetch("/api/auth/addresses/");
}

export function createAddress(address) {
  return apiFetch("/api/auth/addresses/", {
    method: "POST",
    body: {
      label: address.label || undefined,
      line1: address.line1,
      line2: address.line2 || undefined,
      city: address.city,
      state: address.state,
      postal_code: address.postalCode,
      country: address.country,
      is_default: address.isDefault ?? false,
    },
  });
}
