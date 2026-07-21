import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { clearCart, fetchCart, removeCartItem, updateCartItem } from "../../api/cart.js";
import { formatPrice } from "../../utils/format.js";

export default function CartPage() {
  const [cart, setCart] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const load = useCallback(() => {
    setLoading(true);
    fetchCart()
      .then((data) => setCart(data))
      .catch((err) => setError(err))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const handleQuantityChange = async (itemId, quantity) => {
    if (quantity < 1) return;
    await updateCartItem(itemId, { quantity });
    load();
  };

  const handleRemove = async (itemId) => {
    await removeCartItem(itemId);
    load();
  };

  const handleClear = async () => {
    await clearCart();
    load();
  };

  if (loading) return <p>Loading…</p>;
  if (error || !cart) return <div className="alert alert-danger">Couldn&apos;t load your cart.</div>;

  return (
    <div>
      <h1 className="h3 mb-4">Your Cart</h1>
      {cart.items.length === 0 ? (
        <p>
          Your cart is empty. <Link to="/products">Browse products</Link>.
        </p>
      ) : (
        <>
          <table className="table align-middle">
            <thead>
              <tr>
                <th>Product</th>
                <th>Unit price</th>
                <th style={{ width: 140 }}>Quantity</th>
                <th>Line total</th>
                <th />
              </tr>
            </thead>
            <tbody>
              {cart.items.map((item) => (
                <tr key={item.id}>
                  <td>{item.product_name}</td>
                  <td>{formatPrice(item.unit_price)}</td>
                  <td>
                    <input
                      type="number"
                      min="1"
                      className="form-control form-control-sm"
                      value={item.quantity}
                      onChange={(event) => handleQuantityChange(item.id, Number(event.target.value))}
                    />
                  </td>
                  <td>{formatPrice(item.line_total)}</td>
                  <td>
                    <button
                      type="button"
                      className="btn btn-sm btn-outline-danger"
                      onClick={() => handleRemove(item.id)}
                    >
                      Remove
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          <div className="d-flex justify-content-between align-items-center">
            <button type="button" className="btn btn-outline-secondary" onClick={handleClear}>
              Clear cart
            </button>
            <div className="text-end">
              <p className="fs-5 mb-2">
                Subtotal: <strong>{formatPrice(cart.subtotal)}</strong>
              </p>
              <Link to="/checkout" className="btn btn-primary">
                Proceed to checkout
              </Link>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
