const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
const TOKENS_KEY = "auth_tokens";

// Tokens live in localStorage for simplicity — a real production app
// would prefer an httpOnly cookie (immune to XSS reading it via JS),
// but that requires the backend to set cookies cross-origin, which is
// its own can of worms. Acceptable trade-off for this project.
export function getTokens() {
  const raw = localStorage.getItem(TOKENS_KEY);
  return raw ? JSON.parse(raw) : null;
}

export function setTokens(tokens) {
  if (tokens) {
    localStorage.setItem(TOKENS_KEY, JSON.stringify(tokens));
  } else {
    localStorage.removeItem(TOKENS_KEY);
  }
}

export class ApiError extends Error {
  constructor(status, data) {
    super(typeof data?.detail === "string" ? data.detail : "Request failed");
    this.status = status;
    this.data = data;
  }
}

async function parseBody(response) {
  const text = await response.text();
  if (!text) return null;
  try {
    return JSON.parse(text);
  } catch {
    return text;
  }
}

// Refreshing is itself an apiFetch-shaped call, but must never trigger
// another refresh on a 401 (that's how you get infinite recursion) —
// kept as a separate, minimal function rather than reusing apiFetch.
async function refreshAccessToken() {
  const tokens = getTokens();
  if (!tokens?.refresh) return null;

  const response = await fetch(`${API_BASE_URL}/api/auth/login/refresh/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ refresh: tokens.refresh }),
  });
  if (!response.ok) {
    setTokens(null);
    return null;
  }
  // ROTATE_REFRESH_TOKENS=True on the backend means this response
  // carries a new refresh token too, not just a new access token —
  // both must be persisted or the next refresh will use a stale one.
  const data = await parseBody(response);
  setTokens(data);
  return data;
}

/**
 * @param {string} path - e.g. "/api/products/"
 * @param {object} [options]
 * @param {string} [options.method]
 * @param {object} [options.body] - JSON-serialized automatically
 * @param {boolean} [options.auth] - attach the Authorization header (default true)
 * @param {boolean} [options.isFormData] - pass `body` through as-is (FormData) instead of JSON-encoding it
 */
export async function apiFetch(path, { method = "GET", body, auth = true, isFormData = false } = {}) {
  const headers = {};
  if (!isFormData) headers["Content-Type"] = "application/json";

  const tokens = getTokens();
  if (auth && tokens?.access) {
    headers.Authorization = `Bearer ${tokens.access}`;
  }

  const requestInit = {
    method,
    headers,
    body: body === undefined ? undefined : isFormData ? body : JSON.stringify(body),
  };

  let response = await fetch(`${API_BASE_URL}${path}`, requestInit);

  if (response.status === 401 && auth && tokens?.access) {
    const refreshed = await refreshAccessToken();
    if (refreshed) {
      headers.Authorization = `Bearer ${refreshed.access}`;
      response = await fetch(`${API_BASE_URL}${path}`, { ...requestInit, headers });
    }
  }

  const data = await parseBody(response);
  if (!response.ok) {
    throw new ApiError(response.status, data);
  }
  return data;
}
