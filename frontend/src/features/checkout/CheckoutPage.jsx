import { useCallback, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import { createAddress, fetchAddresses } from "../../api/addresses.js";
import { fetchCart } from "../../api/cart.js";
import { checkout } from "../../api/orders.js";
import { verifyPayment } from "../../api/payments.js";
import { useAuth } from "../../context/AuthContext.jsx";
import { formatPrice } from "../../utils/format.js";
import { loadRazorpayScript } from "../../utils/loadRazorpayScript.js";

const emptyAddressForm = { label: "", line1: "", line2: "", city: "", state: "", postalCode: "", country: "" };

export default function CheckoutPage() {
  const { user } = useAuth();
  const navigate = useNavigate();

  const [cart, setCart] = useState(null);
  const [addresses, setAddresses] = useState([]);
  // One address selection is used for both shipping and billing — a
  // deliberate simplification; the backend accepts them independently,
  // but a single "ship & bill here" choice covers the common case
  // without a second selector to fill in.
  const [selectedAddressId, setSelectedAddressId] = useState("");
  const [showAddressForm, setShowAddressForm] = useState(false);
  const [addressForm, setAddressForm] = useState(emptyAddressForm);
  const [couponCode, setCouponCode] = useState("");
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);

  const loadData = useCallback(() => {
    setLoading(true);
    Promise.all([fetchCart(), fetchAddresses()])
      .then(([cartData, addressData]) => {
        setCart(cartData);
        const list = addressData.results ?? addressData;
        setAddresses(list);
        const preferred = list.find((address) => address.is_default) ?? list[0];
        if (preferred) setSelectedAddressId(String(preferred.id));
        setShowAddressForm(list.length === 0);
      })
      .catch((err) => setError(err))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const handleAddressFieldChange = (field) => (event) =>
    setAddressForm((current) => ({ ...current, [field]: event.target.value }));

  const handleCreateAddress = async (event) => {
    event.preventDefault();
    setError(null);
    try {
      const created = await createAddress(addressForm);
      setAddresses((current) => [created, ...current]);
      setSelectedAddressId(String(created.id));
      setShowAddressForm(false);
      setAddressForm(emptyAddressForm);
    } catch (err) {
      setError(err);
    }
  };

  const handlePlaceOrder = async (event) => {
    event.preventDefault();
    if (!selectedAddressId) {
      setError({ message: "Please select or add a shipping address." });
      return;
    }
    setSubmitting(true);
    setError(null);
    try {
      const response = await checkout({
        shippingAddressId: Number(selectedAddressId),
        billingAddressId: Number(selectedAddressId),
        couponCode,
      });

      const scriptLoaded = await loadRazorpayScript();
      if (!scriptLoaded || !window.Razorpay) {
        setError({
          message:
            "Your order was created but the payment widget couldn't load. Check Your Orders to retry.",
        });
        navigate(`/orders/${response.order.id}`, { replace: true });
        return;
      }

      const razorpay = new window.Razorpay({
        key: response.razorpay_key_id,
        amount: Math.round(Number(response.amount) * 100),
        currency: response.currency,
        order_id: response.razorpay_order_id,
        name: "Multi-Vendor Marketplace",
        description: `Order ${response.order.order_number}`,
        prefill: { email: user.email },
        handler: async (razorpayResponse) => {
          try {
            await verifyPayment({
              razorpayOrderId: razorpayResponse.razorpay_order_id,
              razorpayPaymentId: razorpayResponse.razorpay_payment_id,
              razorpaySignature: razorpayResponse.razorpay_signature,
            });
          } catch {
            // Verification failing here doesn't need its own message —
            // the order detail page shows whatever the backend's
            // actual payment status ended up as, which is the source
            // of truth either way.
          }
          navigate(`/orders/${response.order.id}`, { replace: true });
        },
        modal: {
          ondismiss: () => navigate(`/orders/${response.order.id}`, { replace: true }),
        },
      });
      razorpay.open();
    } catch (err) {
      setError(err);
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) return <p>Loading…</p>;
  if (!cart || cart.items.length === 0) {
    return (
      <div>
        <h1 className="h3 mb-3">Checkout</h1>
        <p>Your cart is empty.</p>
      </div>
    );
  }

  return (
    <div className="row g-4">
      <div className="col-12 col-lg-7">
        <h1 className="h3 mb-3">Checkout</h1>

        <h2 className="h5">Shipping &amp; billing address</h2>
        {addresses.length > 0 && !showAddressForm && (
          <div className="mb-3">
            {addresses.map((address) => (
              <div className="form-check mb-2" key={address.id}>
                <input
                  className="form-check-input"
                  type="radio"
                  name="address"
                  id={`address-${address.id}`}
                  value={address.id}
                  checked={selectedAddressId === String(address.id)}
                  onChange={(event) => setSelectedAddressId(event.target.value)}
                />
                <label className="form-check-label" htmlFor={`address-${address.id}`}>
                  {address.label && <strong>{address.label}: </strong>}
                  {address.line1}, {address.city}, {address.state} {address.postal_code}, {address.country}
                </label>
              </div>
            ))}
            <button type="button" className="btn btn-link p-0" onClick={() => setShowAddressForm(true)}>
              + Add a new address
            </button>
          </div>
        )}

        {showAddressForm && (
          <form className="border rounded p-3 mb-3" onSubmit={handleCreateAddress}>
            <div className="row g-2">
              <div className="col-6">
                <input
                  className="form-control"
                  placeholder="Label (optional)"
                  value={addressForm.label}
                  onChange={handleAddressFieldChange("label")}
                />
              </div>
              <div className="col-6">
                <input
                  className="form-control"
                  placeholder="Country code (e.g. US)"
                  value={addressForm.country}
                  onChange={handleAddressFieldChange("country")}
                  required
                  maxLength={2}
                />
              </div>
              <div className="col-12">
                <input
                  className="form-control"
                  placeholder="Address line 1"
                  value={addressForm.line1}
                  onChange={handleAddressFieldChange("line1")}
                  required
                />
              </div>
              <div className="col-12">
                <input
                  className="form-control"
                  placeholder="Address line 2 (optional)"
                  value={addressForm.line2}
                  onChange={handleAddressFieldChange("line2")}
                />
              </div>
              <div className="col-4">
                <input
                  className="form-control"
                  placeholder="City"
                  value={addressForm.city}
                  onChange={handleAddressFieldChange("city")}
                  required
                />
              </div>
              <div className="col-4">
                <input
                  className="form-control"
                  placeholder="State"
                  value={addressForm.state}
                  onChange={handleAddressFieldChange("state")}
                  required
                />
              </div>
              <div className="col-4">
                <input
                  className="form-control"
                  placeholder="Postal code"
                  value={addressForm.postalCode}
                  onChange={handleAddressFieldChange("postalCode")}
                  required
                />
              </div>
            </div>
            <div className="mt-3 d-flex gap-2">
              <button type="submit" className="btn btn-primary btn-sm">
                Save address
              </button>
              {addresses.length > 0 && (
                <button
                  type="button"
                  className="btn btn-outline-secondary btn-sm"
                  onClick={() => setShowAddressForm(false)}
                >
                  Cancel
                </button>
              )}
            </div>
          </form>
        )}

        <h2 className="h5 mt-4">Coupon</h2>
        <input
          className="form-control mb-3"
          style={{ maxWidth: 260 }}
          placeholder="Coupon code (optional)"
          value={couponCode}
          onChange={(event) => setCouponCode(event.target.value)}
        />

        {error && <div className="alert alert-danger">{error.message}</div>}

        <button
          type="button"
          className="btn btn-primary btn-lg"
          onClick={handlePlaceOrder}
          disabled={submitting || !selectedAddressId}
        >
          {submitting ? "Placing order…" : "Place order"}
        </button>
      </div>

      <div className="col-12 col-lg-5">
        <h2 className="h5">Order summary</h2>
        <ul className="list-group mb-3">
          {cart.items.map((item) => (
            <li className="list-group-item d-flex justify-content-between" key={item.id}>
              <span>
                {item.product_name} × {item.quantity}
              </span>
              <span>{formatPrice(item.line_total)}</span>
            </li>
          ))}
          <li className="list-group-item d-flex justify-content-between fw-bold">
            <span>Subtotal</span>
            <span>{formatPrice(cart.subtotal)}</span>
          </li>
        </ul>
        <p className="text-muted small">
          Discounts, shipping, and tax are applied when the order is placed — the final amount charged
          is shown in the payment window.
        </p>
      </div>
    </div>
  );
}
