import { useEffect, useState } from "react";

import { fetchCategories } from "../../api/categories.js";
import { fetchProducts } from "../../api/products.js";
import ProductCard from "./ProductCard.jsx";

export default function ProductListPage() {
  const [products, setProducts] = useState([]);
  const [count, setCount] = useState(0);
  const [page, setPage] = useState(1);
  const [hasNext, setHasNext] = useState(false);
  const [hasPrevious, setHasPrevious] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [categories, setCategories] = useState([]);
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState("");
  const [minPrice, setMinPrice] = useState("");
  const [maxPrice, setMaxPrice] = useState("");

  useEffect(() => {
    // Top-level categories only — good enough for a flat filter dropdown.
    fetchCategories({ parent: "null" })
      .then((data) => setCategories(data.results ?? data))
      .catch(() => setCategories([]));
  }, []);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);
    fetchProducts({ search, category, min_price: minPrice, max_price: maxPrice, page })
      .then((data) => {
        if (cancelled) return;
        const results = data.results ?? data;
        setProducts(results);
        setCount(data.count ?? results.length);
        setHasNext(Boolean(data.next));
        setHasPrevious(Boolean(data.previous));
      })
      .catch((err) => {
        if (!cancelled) setError(err);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [search, category, minPrice, maxPrice, page]);

  // Any filter change resets to page 1 — otherwise a narrower filter
  // could leave the user stranded on a page number past the new
  // (shorter) result set.
  const handleFilterChange = (setter) => (event) => {
    setPage(1);
    setter(event.target.value);
  };

  return (
    <div>
      <h1 className="h3 mb-4">Browse Products</h1>
      <div className="row g-2 mb-4">
        <div className="col-12 col-md-4">
          <input
            className="form-control"
            placeholder="Search products…"
            value={search}
            onChange={handleFilterChange(setSearch)}
          />
        </div>
        <div className="col-6 col-md-3">
          <select className="form-select" value={category} onChange={handleFilterChange(setCategory)}>
            <option value="">All categories</option>
            {categories.map((cat) => (
              <option key={cat.id} value={cat.id}>
                {cat.name}
              </option>
            ))}
          </select>
        </div>
        <div className="col-3 col-md-2">
          <input
            type="number"
            min="0"
            className="form-control"
            placeholder="Min $"
            value={minPrice}
            onChange={handleFilterChange(setMinPrice)}
          />
        </div>
        <div className="col-3 col-md-2">
          <input
            type="number"
            min="0"
            className="form-control"
            placeholder="Max $"
            value={maxPrice}
            onChange={handleFilterChange(setMaxPrice)}
          />
        </div>
      </div>

      {error && <div className="alert alert-danger">Couldn&apos;t load products.</div>}
      {loading ? (
        <p>Loading…</p>
      ) : products.length === 0 ? (
        <p>No products found.</p>
      ) : (
        <>
          <div className="row row-cols-1 row-cols-sm-2 row-cols-lg-4 g-4">
            {products.map((product) => (
              <div className="col" key={product.id}>
                <ProductCard product={product} />
              </div>
            ))}
          </div>
          <nav className="d-flex justify-content-between align-items-center mt-4">
            <button
              type="button"
              className="btn btn-outline-secondary"
              disabled={!hasPrevious}
              onClick={() => setPage((p) => p - 1)}
            >
              Previous
            </button>
            <span className="text-muted">
              Page {page} · {count} product{count === 1 ? "" : "s"}
            </span>
            <button
              type="button"
              className="btn btn-outline-secondary"
              disabled={!hasNext}
              onClick={() => setPage((p) => p + 1)}
            >
              Next
            </button>
          </nav>
        </>
      )}
    </div>
  );
}
