import { Navigate, Outlet, useLocation } from "react-router-dom";

import { useAuth } from "../context/AuthContext.jsx";

/** Gate a nested set of routes behind login, and optionally behind
 * specific roles — e.g. <ProtectedRoute roles={["vendor"]} /> for the
 * vendor dashboard. Unauthenticated visitors are bounced to /login
 * with the page they wanted stashed in router state, so login can
 * send them back afterward. */
export default function ProtectedRoute({ roles }) {
  const { user, isAuthenticated } = useAuth();
  const location = useLocation();

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }
  if (roles && !roles.includes(user.role)) {
    return <Navigate to="/" replace />;
  }
  return <Outlet />;
}
