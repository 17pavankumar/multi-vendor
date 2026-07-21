import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

import { addCartItem } from "../../api/cart.js";
import { fetchProduct } from "../../api/products.js";
import { fetchProductReviews } from "../../api/reviews.js";
import { addWishlistItem } from "../../api/wishlist.js";
import { useAuth } from "../../context/AuthContext.jsx";
import { formatPrice } from "../../utils/format.js";

export default function ProductDetailPage() {
  const { slug } = useParams();
  const { isAuthenticated } = useAuth();
  const [product, setProduct] = useState(null);
  const [loading, setLoading] = useState(true);
  const [notFound, setNotFound] = useState(false);
  const [quantity, setQuantity] = useState(1);
  const [actionMessage, setActionMessage] = useState(null);
  const [reviews, setReviews] = useState([]);

  useEffect(() => {
    setLoading(true);
    setNotFound(false);
    fetchProduct(slug)
      .then((data) => setProduct(data))
      .catch(() => setNotFound(true))
      .finally(() => setLoading(false));
  }, [slug]);

  useEffect(() => {
    if (!product) return;
    fetchProductReviews(product.id)
      .then((data) => setReviews(data.results ?? data))
      .catch(() => setReviews([]));
  }, [product]);

  const handleAddToCart = async (event) => {
    event.preventDefault();
    setActionMessage(null);
    try {
      await addCartItem({ product: product.id, quantity });
      setActionMessage({ type: "success", text: "Added to cart." });
    } catch (err) {
      setActionMessage({ type: "danger", text: err.data?.detail || "Couldn't add to cart." });
    }
  };

  const handleAddToWishlist = async () => {
    setActionMessage(null);
    try {
      await addWishlistItem(product.id);
      setActionMessage({ type: "success", text: "Added to wishlist." });
    } catch (err) {
      setActionMessage({ type: "danger", text: err.data?.detail || "Couldn't add to wishlist." });
    }
  };

  if (loading) return <p>Loading…</p>;
  if (notFound || !product) return <div className="alert alert-danger">Product not found.</div>;

  const primaryImage = product.images?.find((img) => img.is_primary) ?? product.images?.[0];
  const hasDiscount = product.discount_price !== null && product.discount_price !== undefined;

  return (
    <div className="row g-4">
      <div className="col-12 col-md-5">
        <div className="ratio ratio-1x1 bg-light">
          {primaryImage ? (
            <img src={primaryImage.image_url} alt={product.name} className="object-fit-cover" />
          ) : (
            <div className="d-flex align-items-center justify-content-center text-muted">No image</div>
          )}
        </div>
        {product.images?.length > 1 && (
          <div className="d-flex gap-2 mt-2 flex-wrap">
            {product.images.map((img) => (
              <img
                key={img.id}
                src={img.image_url}
                alt={img.alt_text}
                width={64}
                height={64}
                className="object-fit-cover border rounded"
              />
            ))}
          </div>
        )}
      </div>
      <div className="col-12 col-md-7">
        <p className="text-muted mb-1">
          {product.vendor_store_name} · {product.category_name}
        </p>
        <h1 className="h3">{product.name}</h1>
        <p>
          {product.review_count > 0 ? (
            <>
              ★ {product.average_rating} ({product.review_count} review{product.review_count === 1 ? "" : "s"})
            </>
          ) : (
            <span className="text-muted">No reviews yet</span>
          )}
        </p>
        <p className="fs-4">
          {hasDiscount ? (
            <>
              <span className="text-decoration-line-through text-muted me-2">{formatPrice(product.price)}</span>
              <span className="fw-bold">{formatPrice(product.discount_price)}</span>
            </>
          ) : (
            <span className="fw-bold">{formatPrice(product.price)}</span>
          )}
        </p>
        <p>{product.description}</p>

        {isAuthenticated ? (
          <form className="d-flex gap-2 align-items-center mb-2" onSubmit={handleAddToCart}>
            <input
              type="number"
              min="1"
              className="form-control"
              style={{ width: 90 }}
              value={quantity}
              onChange={(event) => setQuantity(Number(event.target.value))}
            />
            <button type="submit" className="btn btn-primary">
              Add to cart
            </button>
            <button type="button" className="btn btn-outline-secondary" onClick={handleAddToWishlist}>
              Add to wishlist
            </button>
          </form>
        ) : (
          <p>
            <Link to="/login">Log in</Link> to purchase or save this item.
          </p>
        )}
        {actionMessage && <div className={`alert alert-${actionMessage.type} py-2`}>{actionMessage.text}</div>}
      </div>

      <div className="col-12">
        <h2 className="h4 mt-4">Reviews</h2>
        {reviews.length === 0 ? (
          <p className="text-muted">No reviews yet.</p>
        ) : (
          <ul className="list-unstyled">
            {reviews.map((review) => (
              <li key={review.id} className="border-bottom py-2">
                <strong>{review.customer_name}</strong> — {"★".repeat(review.rating)}
                {review.title && <div className="fw-semibold">{review.title}</div>}
                <p className="mb-0">{review.body}</p>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
