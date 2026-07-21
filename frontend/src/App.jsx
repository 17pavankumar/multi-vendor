import { Route, Routes } from "react-router-dom";

import Layout from "./components/Layout.jsx";
import LoginPage from "./features/auth/LoginPage.jsx";
import RegisterPage from "./features/auth/RegisterPage.jsx";
import HomePage from "./pages/HomePage.jsx";
import NotFoundPage from "./pages/NotFoundPage.jsx";

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<HomePage />} />
        <Route path="login" element={<LoginPage />} />
        <Route path="register" element={<RegisterPage />} />
        {/* Protected, role-gated routes (browse/cart/checkout, vendor
            dashboard, admin dashboard) land here in later sub-phases,
            each wrapped in <ProtectedRoute roles={[...]} />. */}
        <Route path="*" element={<NotFoundPage />} />
      </Route>
    </Routes>
  );
}
