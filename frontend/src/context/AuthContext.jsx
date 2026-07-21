import { createContext, useCallback, useContext, useState } from "react";

import * as authApi from "../api/auth.js";
import { getTokens, setTokens as persistTokens } from "../api/client.js";
import { decodeJwtPayload } from "../utils/jwt.js";

const AuthContext = createContext(null);

// The access token itself carries role + email (see the backend's
// RoleTokenObtainPairSerializer) — decoding it locally means the
// logged-in user's identity is known immediately on login/refresh,
// with no extra round-trip to /api/auth/profile/.
function userFromTokens(tokens) {
  if (!tokens?.access) return null;
  const payload = decodeJwtPayload(tokens.access);
  if (!payload) return null;
  return { id: payload.user_id, email: payload.email, role: payload.role };
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => userFromTokens(getTokens()));
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const login = useCallback(async ({ email, password }) => {
    setLoading(true);
    setError(null);
    try {
      const tokens = await authApi.login({ email, password });
      persistTokens(tokens);
      setUser(userFromTokens(tokens));
      return true;
    } catch (err) {
      setError(err);
      return false;
    } finally {
      setLoading(false);
    }
  }, []);

  const register = useCallback(
    async (fields) => {
      setLoading(true);
      setError(null);
      try {
        await authApi.register(fields);
      } catch (err) {
        setError(err);
        setLoading(false);
        return false;
      }
      // Registration doesn't return tokens itself — log in right after
      // with the same credentials, one less step for the user.
      return login({ email: fields.email, password: fields.password });
    },
    [login],
  );

  const logout = useCallback(() => {
    persistTokens(null);
    setUser(null);
  }, []);

  const value = { user, loading, error, login, register, logout, isAuthenticated: Boolean(user) };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within an AuthProvider");
  return ctx;
}
