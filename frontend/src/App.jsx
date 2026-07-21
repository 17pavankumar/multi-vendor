import { Route, Routes } from "react-router-dom";

import Layout from "./components/Layout.jsx";
import ProtectedRoute from "./components/ProtectedRoute.jsx";
import LoginPage from "./features/auth/LoginPage.jsx";
import RegisterPage from "./features/auth/RegisterPage.jsx";
import CartPage from "./features/cart/CartPage.jsx";
import ProductDetailPage from "./features/products/ProductDetailPage.jsx";
import ProductListPage from "./features/products/ProductListPage.jsx";
import WishlistPage from "./features/wishlist/WishlistPage.jsx";
import HomePage from "./pages/HomePage.jsx";
import NotFoundPage from "./pages/NotFoundPage.jsx";

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<HomePage />} />
        <Route path="login" element={<LoginPage />} />
        <Route path="register" element={<RegisterPage />} />
        <Route path="products" element={<ProductListPage />} />
        <Route path="products/:slug" element={<ProductDetailPage />} />
        {/* Cart/wishlist are open to any authenticated role (customer,
            vendor, or admin) on the backend, so no `roles` restriction
            here — vendor/admin dashboards (later sub-phases) will use
            <ProtectedRoute roles={[...]} /> instead. */}
        <Route element={<ProtectedRoute />}>
          <Route path="cart" element={<CartPage />} />
          <Route path="wishlist" element={<WishlistPage />} />
        </Route>
        <Route path="*" element={<NotFoundPage />} />
      </Route>
    </Routes>
  );
}
