import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { useAuth } from "../../context/AuthContext.jsx";

const initialForm = { email: "", password: "", firstName: "", lastName: "", phone: "" };

function FieldError({ messages }) {
  if (!messages) return null;
  return <div className="text-danger small mt-1">{messages.join(" ")}</div>;
}

export default function RegisterPage() {
  const { register, loading, error } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState(initialForm);

  const handleChange = (field) => (event) => setForm((current) => ({ ...current, [field]: event.target.value }));

  const handleSubmit = async (event) => {
    event.preventDefault();
    const ok = await register(form);
    if (ok) navigate("/", { replace: true });
  };

  // DRF validation errors arrive as {field_name: ["message", ...]} —
  // shown next to each field; anything else (network failure, a
  // non-field error) falls back to the generic alert below.
  const fieldErrors = error?.data && typeof error.data === "object" ? error.data : null;

  return (
    <div className="row justify-content-center">
      <div className="col-12 col-sm-9 col-md-7 col-lg-5">
        <h1 className="h3 mb-3">Create your account</h1>
        <form onSubmit={handleSubmit} noValidate>
          <div className="row">
            <div className="col-6 mb-3">
              <label className="form-label" htmlFor="firstName">
                First name
              </label>
              <input
                id="firstName"
                className="form-control"
                value={form.firstName}
                onChange={handleChange("firstName")}
                required
                autoComplete="given-name"
              />
              <FieldError messages={fieldErrors?.first_name} />
            </div>
            <div className="col-6 mb-3">
              <label className="form-label" htmlFor="lastName">
                Last name
              </label>
              <input
                id="lastName"
                className="form-control"
                value={form.lastName}
                onChange={handleChange("lastName")}
                required
                autoComplete="family-name"
              />
              <FieldError messages={fieldErrors?.last_name} />
            </div>
          </div>
          <div className="mb-3">
            <label className="form-label" htmlFor="email">
              Email
            </label>
            <input
              id="email"
              type="email"
              className="form-control"
              value={form.email}
              onChange={handleChange("email")}
              required
              autoComplete="email"
            />
            <FieldError messages={fieldErrors?.email} />
          </div>
          <div className="mb-3">
            <label className="form-label" htmlFor="phone">
              Phone (optional)
            </label>
            <input
              id="phone"
              className="form-control"
              value={form.phone}
              onChange={handleChange("phone")}
              autoComplete="tel"
            />
            <FieldError messages={fieldErrors?.phone} />
          </div>
          <div className="mb-3">
            <label className="form-label" htmlFor="password">
              Password
            </label>
            <input
              id="password"
              type="password"
              className="form-control"
              value={form.password}
              onChange={handleChange("password")}
              required
              autoComplete="new-password"
            />
            <FieldError messages={fieldErrors?.password} />
          </div>
          {error && !fieldErrors && <div className="alert alert-danger py-2">{error.message}</div>}
          <button type="submit" className="btn btn-primary w-100" disabled={loading}>
            {loading ? "Creating account…" : "Sign up"}
          </button>
        </form>
        <p className="mt-3 text-center">
          Already have an account? <Link to="/login">Log in</Link>
        </p>
      </div>
    </div>
  );
}
