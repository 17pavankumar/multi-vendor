import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { addCartItem } from "../../api/cart.js";
import { fetchWishlist, removeWishlistItem } from "../../api/wishlist.js";
import { formatPrice } from "../../utils/format.js";

export default function WishlistPage() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [message, setMessage] = useState(null);

  const load = useCallback(() => {
    setLoading(true);
    fetchWishlist()
      .then((data) => setItems(data.results ?? data))
      .catch((err) => setError(err))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const handleRemove = async (id) => {
    await removeWishlistItem(id);
    load();
  };

  const handleAddToCart = async (productId) => {
    setMessage(null);
    try {
      await addCartItem({ product: productId, quantity: 1 });
      setMessage({ type: "success", text: "Added to cart." });
    } catch (err) {
      setMessage({ type: "danger", text: err.data?.detail || "Couldn't add to cart." });
    }
  };

  if (loading) return <p>Loading…</p>;
  if (error) return <div className="alert alert-danger">Couldn&apos;t load your wishlist.</div>;

  return (
    <div>
      <h1 className="h3 mb-4">Your Wishlist</h1>
      {message && <div className={`alert alert-${message.type} py-2`}>{message.text}</div>}
      {items.length === 0 ? (
        <p>
          Your wishlist is empty. <Link to="/products">Browse products</Link>.
        </p>
      ) : (
        <div className="row row-cols-1 row-cols-sm-2 row-cols-lg-3 g-3">
          {items.map((item) => (
            <div className="col" key={item.id}>
              <div className="card h-100">
                <div className="card-body">
                  <h2 className="h6 card-title">{item.product_name}</h2>
                  <p className="card-text fw-bold">{formatPrice(item.product_price)}</p>
                  <div className="d-flex gap-2">
                    <button
                      type="button"
                      className="btn btn-sm btn-primary"
                      onClick={() => handleAddToCart(item.product)}
                    >
                      Add to cart
                    </button>
                    <button
                      type="button"
                      className="btn btn-sm btn-outline-danger"
                      onClick={() => handleRemove(item.id)}
                    >
                      Remove
                    </button>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
