import { apiFetch } from "./client.js";

export function register({ email, password, firstName, lastName, phone }) {
  return apiFetch("/api/auth/register/", {
    method: "POST",
    auth: false,
    body: {
      email,
      password,
      first_name: firstName,
      last_name: lastName,
      phone: phone || undefined,
    },
  });
}

export function login({ email, password }) {
  return apiFetch("/api/auth/login/", {
    method: "POST",
    auth: false,
    body: { email, password },
  });
}

export function fetchProfile() {
  return apiFetch("/api/auth/profile/");
}
