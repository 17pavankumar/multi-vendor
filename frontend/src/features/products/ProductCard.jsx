import { Link } from "react-router-dom";

import { formatPrice } from "../../utils/format.js";

export default function ProductCard({ product }) {
  const hasDiscount = product.discount_price !== null && product.discount_price !== undefined;

  return (
    <Link to={`/products/${product.slug}`} className="text-decoration-none text-reset">
      <div className="card h-100">
        <div className="ratio ratio-1x1 bg-light">
          {product.primary_image ? (
            <img src={product.primary_image} alt={product.name} className="object-fit-cover" />
          ) : (
            <div className="d-flex align-items-center justify-content-center text-muted small">No image</div>
          )}
        </div>
        <div className="card-body">
          <p className="text-muted small mb-1">{product.vendor_store_name}</p>
          <h2 className="h6 card-title">{product.name}</h2>
          <p className="card-text">
            {hasDiscount ? (
              <>
                <span className="text-decoration-line-through text-muted me-2">{formatPrice(product.price)}</span>
                <span className="fw-bold">{formatPrice(product.discount_price)}</span>
              </>
            ) : (
              <span className="fw-bold">{formatPrice(product.price)}</span>
            )}
          </p>
        </div>
      </div>
    </Link>
  );
}
