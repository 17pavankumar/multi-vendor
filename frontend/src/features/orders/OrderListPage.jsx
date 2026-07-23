import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { fetchOrders } from "../../api/orders.js";
import { formatPrice } from "../../utils/format.js";

export default function OrderListPage() {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchOrders()
      .then((data) => setOrders(data.results ?? data))
      .catch((err) => setError(err))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <p>Loading…</p>;
  if (error) return <div className="alert alert-danger">Couldn&apos;t load your orders.</div>;

  return (
    <div>
      <h1 className="h3 mb-4">Your Orders</h1>
      {orders.length === 0 ? (
        <p>
          No orders yet. <Link to="/products">Browse products</Link>.
        </p>
      ) : (
        <table className="table align-middle">
          <thead>
            <tr>
              <th>Order</th>
              <th>Placed</th>
              <th>Status</th>
              <th>Total</th>
              <th />
            </tr>
          </thead>
          <tbody>
            {orders.map((order) => (
              <tr key={order.id}>
                <td className="text-muted small">{order.order_number}</td>
                <td>{new Date(order.placed_at).toLocaleDateString()}</td>
                <td>
                  <span className="badge text-bg-secondary text-uppercase">{order.status}</span>
                </td>
                <td>{formatPrice(order.total_amount)}</td>
                <td>
                  <Link to={`/orders/${order.id}`} className="btn btn-sm btn-outline-primary">
                    View
                  </Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
