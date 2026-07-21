import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";

import { useAuth } from "../../context/AuthContext.jsx";

export default function LoginPage() {
  const { login, loading, error } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const handleSubmit = async (event) => {
    event.preventDefault();
    const ok = await login({ email, password });
    if (ok) {
      navigate(location.state?.from?.pathname || "/", { replace: true });
    }
  };

  return (
    <div className="row justify-content-center">
      <div className="col-12 col-sm-8 col-md-6 col-lg-4">
        <h1 className="h3 mb-3">Log in</h1>
        <form onSubmit={handleSubmit} noValidate>
          <div className="mb-3">
            <label className="form-label" htmlFor="email">
              Email
            </label>
            <input
              id="email"
              type="email"
              className="form-control"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              required
              autoComplete="email"
            />
          </div>
          <div className="mb-3">
            <label className="form-label" htmlFor="password">
              Password
            </label>
            <input
              id="password"
              type="password"
              className="form-control"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              required
              autoComplete="current-password"
            />
          </div>
          {error && <div className="alert alert-danger py-2">{error.message}</div>}
          <button type="submit" className="btn btn-primary w-100" disabled={loading}>
            {loading ? "Logging in…" : "Log in"}
          </button>
        </form>
        <p className="mt-3 text-center">
          Don&apos;t have an account? <Link to="/register">Sign up</Link>
        </p>
      </div>
    </div>
  );
}
