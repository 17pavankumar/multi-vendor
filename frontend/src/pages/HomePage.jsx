import { Link } from "react-router-dom";

import { useAuth } from "../context/AuthContext.jsx";

export default function HomePage() {
  const { user, isAuthenticated } = useAuth();

  return (
    <div>
      <h1 className="h3">Welcome to the Multi-Vendor Marketplace</h1>
      {isAuthenticated ? (
        <p>
          You&apos;re logged in as <strong>{user.email}</strong>{" "}
          <span className="badge text-bg-secondary text-uppercase">{user.role}</span>.
        </p>
      ) : (
        <p>
          <Link to="/login">Log in</Link> or <Link to="/register">sign up</Link> to get started.
        </p>
      )}
    </div>
  );
}
