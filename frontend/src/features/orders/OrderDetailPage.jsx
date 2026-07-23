import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";

import { fetchOrder } from "../../api/orders.js";
import { formatPrice } from "../../utils/format.js";

export default function OrderDetailPage() {
  const { id } = useParams();
  const [order, setOrder] = useState(null);
  const [loading, setLoading] = useState(true);
  const [notFound, setNotFound] = useState(false);

  useEffect(() => {
    setLoading(true);
    setNotFound(false);
    fetchOrder(id)
      .then((data) => setOrder(data))
      .catch(() => setNotFound(true))
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) return <p>Loading…</p>;
  if (notFound || !order) return <div className="alert alert-danger">Order not found.</div>;

  return (
    <div>
      <h1 className="h3 mb-1">Order {order.order_number}</h1>
      <p className="mb-4">
        Status: <span className="badge text-bg-secondary text-uppercase">{order.status}</span>
      </p>

      <table className="table align-middle">
        <thead>
          <tr>
            <th>Product</th>
            <th>Vendor</th>
            <th>Qty</th>
            <th>Unit price</th>
            <th>Subtotal</th>
            <th>Fulfillment</th>
          </tr>
        </thead>
        <tbody>
          {order.items.map((item) => (
            <tr key={item.id}>
              <td>{item.product_name}</td>
              <td>{item.vendor_store_name}</td>
              <td>{item.quantity}</td>
              <td>{formatPrice(item.unit_price)}</td>
              <td>{formatPrice(item.subtotal)}</td>
              <td>
                <span className="badge text-bg-light text-uppercase">{item.fulfillment_status}</span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      <div className="row justify-content-end">
        <div className="col-12 col-md-4">
          <dl className="row mb-0">
            <dt className="col-8">Subtotal</dt>
            <dd className="col-4 text-end">{formatPrice(order.subtotal)}</dd>
            <dt className="col-8">Discount</dt>
            <dd className="col-4 text-end">-{formatPrice(order.discount_amount)}</dd>
            <dt className="col-8">Shipping</dt>
            <dd className="col-4 text-end">{formatPrice(order.shipping_amount)}</dd>
            <dt className="col-8">Tax</dt>
            <dd className="col-4 text-end">{formatPrice(order.tax_amount)}</dd>
            <dt className="col-8 fw-bold">Total</dt>
            <dd className="col-4 text-end fw-bold">{formatPrice(order.total_amount)}</dd>
          </dl>
        </div>
      </div>
    </div>
  );
}
