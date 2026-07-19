-- =====================================================================
-- Multi-Vendor E-Commerce — MySQL 8 Schema
-- =====================================================================
-- This file is the single source of truth for the relational model.
-- Django migrations (generated later, per app) will produce equivalent
-- tables — this file exists so the schema can be read/reviewed as one
-- whole, independent of ORM code.
--
-- Conventions used throughout:
--   * Every table has a BIGINT AUTO_INCREMENT surrogate key named `id`.
--   * created_at / updated_at store UTC. `updated_at` uses
--     "ON UPDATE CURRENT_TIMESTAMP" so MySQL refreshes it automatically
--     on every UPDATE — no application code has to remember to set it.
--   * Foreign keys are named `<referenced_table_singular>_id`.
--   * Every table is InnoDB — MySQL's only engine that enforces foreign
--     keys and CHECK constraints; MyISAM silently ignores both.
--   * ON DELETE behaviour is chosen per relationship (see comments) —
--     never left to the default (RESTRICT) without thinking about it.
--   * Money columns are DECIMAL(10,2), never FLOAT — floats lose cents.
--   * Enums are CHECK constraints on VARCHAR, not MySQL's native ENUM
--     type, because adding a value to a CHECK list is a metadata-only
--     ALTER; widening a native ENUM still requires a table rebuild.
--     CHECK constraints are enforced as of MySQL 8.0.16 — this schema
--     targets 8.0.16+.
-- =====================================================================

CREATE DATABASE IF NOT EXISTS multivendor
    CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci; -- _ai_ci = accent- and case-insensitive, so 'a@b.com' = 'A@B.com'
USE multivendor;


-- =====================================================================
-- 1. USERS & AUTH
-- =====================================================================

-- One table for all humans in the system. `role` distinguishes
-- customer / vendor / admin instead of three separate tables, because
-- every role shares the same login/auth fields — a vendor is a user
-- who *also* owns a row in vendor_profiles.
CREATE TABLE users (
    id              BIGINT AUTO_INCREMENT PRIMARY KEY,
    email           VARCHAR(255) NOT NULL,   -- table's ci collation makes this lookup case-insensitive
    password_hash   VARCHAR(255) NOT NULL,
    first_name      VARCHAR(100) NOT NULL,
    last_name       VARCHAR(100) NOT NULL,
    phone           VARCHAR(20),
    role            VARCHAR(20) NOT NULL CHECK (role IN ('customer', 'vendor', 'admin')),
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    is_verified     BOOLEAN NOT NULL DEFAULT FALSE,
    created_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uq_users_email (email),
    KEY idx_users_role (role)
) ENGINE=InnoDB;

-- A user can have multiple shipping/billing addresses. Deleting a user
-- cascades here — an address is meaningless without its owner.
CREATE TABLE addresses (
    id              BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id         BIGINT NOT NULL,
    label           VARCHAR(50),              -- "Home", "Office"
    line1           VARCHAR(255) NOT NULL,
    line2           VARCHAR(255),
    city            VARCHAR(100) NOT NULL,
    state           VARCHAR(100) NOT NULL,
    postal_code     VARCHAR(20) NOT NULL,
    country         VARCHAR(2)  NOT NULL,     -- ISO 3166-1 alpha-2
    is_default      BOOLEAN NOT NULL DEFAULT FALSE,
    created_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    KEY idx_addresses_user (user_id),
    CONSTRAINT fk_addresses_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;


-- =====================================================================
-- 2. VENDORS
-- =====================================================================

-- Extends a user with store-front data. One-to-one via UNIQUE user_id.
-- Kept separate from `users` (rather than adding store columns to
-- users) because most of these fields are NULL for 99% of rows
-- (customers) — a separate table avoids a sparse users table and lets
-- vendor approval evolve independently.
CREATE TABLE vendor_profiles (
    id                  BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id             BIGINT NOT NULL,
    store_name          VARCHAR(150) NOT NULL,
    store_slug          VARCHAR(160) NOT NULL,
    description         TEXT,
    logo_url            VARCHAR(500),
    status              VARCHAR(20) NOT NULL DEFAULT 'pending'
                            CHECK (status IN ('pending', 'approved', 'rejected', 'suspended')),
    default_commission_rate DECIMAL(5,2) NOT NULL DEFAULT 10.00, -- percent
    approved_by         BIGINT,               -- admin user who approved
    approved_at         DATETIME,
    created_at          DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at          DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uq_vendor_profiles_user (user_id),
    UNIQUE KEY uq_vendor_profiles_slug (store_slug),
    KEY idx_vendor_profiles_status (status),
    CONSTRAINT fk_vendor_profiles_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_vendor_profiles_approver FOREIGN KEY (approved_by) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB;


-- =====================================================================
-- 3. CATALOG: categories, products, images, inventory
-- =====================================================================

-- Self-referencing tree for nested categories (Electronics > Phones).
-- parent_id NULL = top-level category.
CREATE TABLE categories (
    id          BIGINT AUTO_INCREMENT PRIMARY KEY,
    parent_id   BIGINT,
    name        VARCHAR(100) NOT NULL,
    slug        VARCHAR(120) NOT NULL,
    image_url   VARCHAR(500),
    created_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_categories_slug (slug),
    KEY idx_categories_parent (parent_id),
    CONSTRAINT fk_categories_parent FOREIGN KEY (parent_id) REFERENCES categories(id) ON DELETE SET NULL
) ENGINE=InnoDB;

CREATE TABLE products (
    id              BIGINT AUTO_INCREMENT PRIMARY KEY,
    vendor_id       BIGINT NOT NULL,
    category_id     BIGINT NOT NULL,
    name            VARCHAR(200) NOT NULL,
    slug            VARCHAR(220) NOT NULL,
    description     TEXT,
    price           DECIMAL(10,2) NOT NULL CHECK (price >= 0),
    discount_price  DECIMAL(10,2) CHECK (discount_price >= 0),
    sku             VARCHAR(64) NOT NULL,
    status          VARCHAR(20) NOT NULL DEFAULT 'draft'
                        CHECK (status IN ('draft', 'active', 'archived')),
    created_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uq_products_slug (slug),
    UNIQUE KEY uq_products_sku (sku),
    KEY idx_products_vendor (vendor_id),
    KEY idx_products_category (category_id),
    KEY idx_products_status (status),
    CONSTRAINT chk_discount_lt_price CHECK (discount_price IS NULL OR discount_price <= price),
    CONSTRAINT fk_products_vendor FOREIGN KEY (vendor_id) REFERENCES vendor_profiles(id) ON DELETE CASCADE,
    -- RESTRICT: a category with products in it can't be deleted out from under them
    CONSTRAINT fk_products_category FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE RESTRICT
) ENGINE=InnoDB;

CREATE TABLE product_images (
    id                  BIGINT AUTO_INCREMENT PRIMARY KEY,
    product_id          BIGINT NOT NULL,
    image_url           VARCHAR(500) NOT NULL,
    alt_text            VARCHAR(255),
    is_primary          BOOLEAN NOT NULL DEFAULT FALSE,
    -- Generated column: equals product_id when this row is the primary
    -- image, otherwise NULL. MySQL's UNIQUE index allows unlimited NULLs
    -- but only one row per non-NULL value — so this enforces "at most
    -- one primary image per product" without a native partial index
    -- (which MySQL doesn't support, unlike Postgres).
    primary_of_product  BIGINT GENERATED ALWAYS AS (IF(is_primary, product_id, NULL)) STORED,
    sort_order          SMALLINT NOT NULL DEFAULT 0,
    KEY idx_product_images_product (product_id),
    UNIQUE KEY uq_product_images_primary (primary_of_product),
    CONSTRAINT fk_product_images_product FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Separate table (not a `quantity` column on products) because stock
-- changes at a much higher write frequency than product metadata, and
-- because reserved_quantity needs row-level locking during checkout
-- (SELECT ... FOR UPDATE) without locking the whole product row.
CREATE TABLE inventory (
    id                  BIGINT AUTO_INCREMENT PRIMARY KEY,
    product_id          BIGINT NOT NULL,
    quantity            INT NOT NULL DEFAULT 0 CHECK (quantity >= 0),
    reserved_quantity   INT NOT NULL DEFAULT 0 CHECK (reserved_quantity >= 0),
    low_stock_threshold INT NOT NULL DEFAULT 5,
    updated_at          DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uq_inventory_product (product_id),
    CONSTRAINT chk_reserved_lte_quantity CHECK (reserved_quantity <= quantity),
    CONSTRAINT fk_inventory_product FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
) ENGINE=InnoDB;


-- =====================================================================
-- 4. CART & WISHLIST
-- =====================================================================

CREATE TABLE carts (
    id          BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id     BIGINT NOT NULL,
    created_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uq_carts_user (user_id),
    CONSTRAINT fk_carts_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE cart_items (
    id          BIGINT AUTO_INCREMENT PRIMARY KEY,
    cart_id     BIGINT NOT NULL,
    product_id  BIGINT NOT NULL,
    quantity    INT NOT NULL CHECK (quantity > 0),
    -- unit_price is captured at add-to-cart time so a vendor changing
    -- the price mid-session doesn't silently change the customer's cart total.
    unit_price  DECIMAL(10,2) NOT NULL,
    created_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_cart_items_cart_product (cart_id, product_id),
    KEY idx_cart_items_cart (cart_id),
    CONSTRAINT fk_cart_items_cart FOREIGN KEY (cart_id) REFERENCES carts(id) ON DELETE CASCADE,
    CONSTRAINT fk_cart_items_product FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE wishlists (
    id          BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id     BIGINT NOT NULL,
    product_id  BIGINT NOT NULL,
    created_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_wishlists_user_product (user_id, product_id),
    KEY idx_wishlists_user (user_id),
    CONSTRAINT fk_wishlists_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_wishlists_product FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
) ENGINE=InnoDB;


-- =====================================================================
-- 5. COUPONS
-- =====================================================================

-- vendor_id NULL = platform-wide coupon issued by admin.
CREATE TABLE coupons (
    id                  BIGINT AUTO_INCREMENT PRIMARY KEY,
    vendor_id           BIGINT,
    code                VARCHAR(32) NOT NULL,
    discount_type       VARCHAR(10) NOT NULL CHECK (discount_type IN ('percent', 'fixed')),
    discount_value      DECIMAL(10,2) NOT NULL CHECK (discount_value > 0),
    min_order_amount    DECIMAL(10,2) NOT NULL DEFAULT 0,
    max_discount_amount DECIMAL(10,2),        -- caps a % discount, e.g. "20% off up to $50"
    usage_limit         INT,                   -- NULL = unlimited
    usage_count         INT NOT NULL DEFAULT 0,
    valid_from          DATETIME NOT NULL,
    valid_until         DATETIME NOT NULL,
    is_active           BOOLEAN NOT NULL DEFAULT TRUE,
    created_at          DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_coupons_code (code),
    KEY idx_coupons_vendor (vendor_id),
    CONSTRAINT chk_coupon_dates CHECK (valid_until > valid_from),
    CONSTRAINT fk_coupons_vendor FOREIGN KEY (vendor_id) REFERENCES vendor_profiles(id) ON DELETE CASCADE
) ENGINE=InnoDB;


-- =====================================================================
-- 6. ORDERS
-- =====================================================================
-- (coupon_redemptions lives here, not in section 5, because a foreign
-- key's referenced table must already exist — it can't forward-
-- reference `orders` before this point.)

CREATE TABLE orders (
    id                  BIGINT AUTO_INCREMENT PRIMARY KEY,
    -- Public-facing order identifier shown to customers/receipts, kept
    -- separate from the internal auto-increment `id` so sequential IDs
    -- (and order volume) are never exposed in a URL. Generated in
    -- application code with Python's uuid4() before INSERT — MySQL has
    -- no built-in UUID default prior to 8.0.13's expression defaults,
    -- and even there it isn't available on all managed MySQL hosts.
    order_number        CHAR(36) NOT NULL,
    user_id             BIGINT NOT NULL,
    status              VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (
                            status IN ('pending', 'paid', 'processing', 'shipped',
                                       'delivered', 'cancelled', 'refunded')
                        ),
    subtotal            DECIMAL(10,2) NOT NULL,
    discount_amount     DECIMAL(10,2) NOT NULL DEFAULT 0,
    shipping_amount     DECIMAL(10,2) NOT NULL DEFAULT 0,
    tax_amount          DECIMAL(10,2) NOT NULL DEFAULT 0,
    total_amount        DECIMAL(10,2) NOT NULL,
    shipping_address_id BIGINT NOT NULL,
    billing_address_id  BIGINT NOT NULL,
    placed_at           DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at          DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uq_orders_order_number (order_number),
    KEY idx_orders_user (user_id),
    KEY idx_orders_status (status),
    -- RESTRICT on user_id/addresses: never let deleting a user or
    -- address silently destroy order history; app must archive first.
    CONSTRAINT fk_orders_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE RESTRICT,
    CONSTRAINT fk_orders_shipping_address FOREIGN KEY (shipping_address_id) REFERENCES addresses(id) ON DELETE RESTRICT,
    CONSTRAINT fk_orders_billing_address FOREIGN KEY (billing_address_id) REFERENCES addresses(id) ON DELETE RESTRICT
) ENGINE=InnoDB;

-- A single order can contain products from multiple vendors. Each line
-- item is priced/tracked independently since fulfillment and
-- commission are per-vendor, not per-order.
CREATE TABLE order_items (
    id                  BIGINT AUTO_INCREMENT PRIMARY KEY,
    order_id            BIGINT NOT NULL,
    product_id          BIGINT NOT NULL,
    vendor_id           BIGINT NOT NULL,
    quantity            INT NOT NULL CHECK (quantity > 0),
    unit_price          DECIMAL(10,2) NOT NULL,
    discount_amount     DECIMAL(10,2) NOT NULL DEFAULT 0,
    subtotal            DECIMAL(10,2) NOT NULL,           -- (unit_price * quantity) - discount_amount
    commission_rate     DECIMAL(5,2) NOT NULL,             -- snapshotted at order time
    commission_amount   DECIMAL(10,2) NOT NULL,
    fulfillment_status  VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (
                            fulfillment_status IN ('pending', 'packed', 'shipped', 'delivered', 'cancelled')
                        ),
    KEY idx_order_items_order (order_id),
    KEY idx_order_items_vendor (vendor_id),
    CONSTRAINT fk_order_items_order FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    CONSTRAINT fk_order_items_product FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE RESTRICT,
    CONSTRAINT fk_order_items_vendor FOREIGN KEY (vendor_id) REFERENCES vendor_profiles(id) ON DELETE RESTRICT
) ENGINE=InnoDB;

-- Tracks which order redeemed which coupon — needed to enforce
-- per-user usage limits and to audit discount totals.
CREATE TABLE coupon_redemptions (
    id              BIGINT AUTO_INCREMENT PRIMARY KEY,
    coupon_id       BIGINT NOT NULL,
    order_id        BIGINT NOT NULL,
    user_id         BIGINT NOT NULL,
    discount_amount DECIMAL(10,2) NOT NULL,
    created_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_coupon_redemptions_coupon_order (coupon_id, order_id),
    KEY idx_coupon_redemptions_order (order_id),
    CONSTRAINT fk_coupon_redemptions_coupon FOREIGN KEY (coupon_id) REFERENCES coupons(id) ON DELETE CASCADE,
    CONSTRAINT fk_coupon_redemptions_order FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    CONSTRAINT fk_coupon_redemptions_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;


-- =====================================================================
-- 7. SHIPPING / LIVE TRACKING
-- =====================================================================

-- One shipment per vendor per order (a multi-vendor order ships as N
-- separate packages). shipment_tracking_events gives the live-tracking timeline.
CREATE TABLE shipments (
    id                  BIGINT AUTO_INCREMENT PRIMARY KEY,
    order_id            BIGINT NOT NULL,
    vendor_id           BIGINT NOT NULL,
    carrier             VARCHAR(100),
    tracking_number     VARCHAR(100),
    status              VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (
                            status IN ('pending', 'shipped', 'in_transit', 'out_for_delivery', 'delivered', 'failed')
                        ),
    shipped_at          DATETIME,
    delivered_at        DATETIME,
    estimated_delivery  DATE,
    KEY idx_shipments_order (order_id),
    KEY idx_shipments_vendor (vendor_id),
    CONSTRAINT fk_shipments_order FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    CONSTRAINT fk_shipments_vendor FOREIGN KEY (vendor_id) REFERENCES vendor_profiles(id) ON DELETE RESTRICT
) ENGINE=InnoDB;

CREATE TABLE shipment_tracking_events (
    id              BIGINT AUTO_INCREMENT PRIMARY KEY,
    shipment_id     BIGINT NOT NULL,
    status          VARCHAR(50) NOT NULL,
    location        VARCHAR(150),
    note            TEXT,
    occurred_at     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    KEY idx_tracking_events_shipment (shipment_id),
    CONSTRAINT fk_tracking_events_shipment FOREIGN KEY (shipment_id) REFERENCES shipments(id) ON DELETE CASCADE
) ENGINE=InnoDB;


-- =====================================================================
-- 8. PAYMENTS — Razorpay
-- =====================================================================
-- Razorpay's flow is: create an `order` on Razorpay's side first
-- (razorpay_order_id), collect payment client-side, then Razorpay
-- calls our webhook with a `payment` object (razorpay_payment_id) and
-- a signature we verify server-side. This table stores both IDs plus
-- the raw verification state so a webhook replay or dispute can be
-- audited without calling Razorpay's API again.
CREATE TABLE payments (
    id                      BIGINT AUTO_INCREMENT PRIMARY KEY,
    order_id                BIGINT NOT NULL,
    razorpay_order_id       VARCHAR(64) NOT NULL,
    razorpay_payment_id     VARCHAR(64),
    razorpay_signature      VARCHAR(128),
    amount                  DECIMAL(10,2) NOT NULL,
    currency                VARCHAR(3) NOT NULL DEFAULT 'INR',
    status                  VARCHAR(20) NOT NULL DEFAULT 'created' CHECK (
                                status IN ('created', 'authorized', 'captured', 'failed', 'refunded')
                            ),
    method                  VARCHAR(30),        -- card, upi, netbanking, wallet (from Razorpay webhook payload)
    error_code              VARCHAR(50),
    error_description       TEXT,
    created_at              DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at              DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uq_payments_razorpay_order_id (razorpay_order_id),
    KEY idx_payments_order (order_id),
    KEY idx_payments_status (status),
    CONSTRAINT fk_payments_order FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE RESTRICT
) ENGINE=InnoDB;

-- Refunds are modeled separately from payments because Razorpay
-- supports partial refunds — one payment can have several refund rows.
CREATE TABLE refunds (
    id                  BIGINT AUTO_INCREMENT PRIMARY KEY,
    payment_id          BIGINT NOT NULL,
    razorpay_refund_id  VARCHAR(64) NOT NULL,
    amount              DECIMAL(10,2) NOT NULL CHECK (amount > 0),
    status              VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'processed', 'failed')),
    reason              TEXT,
    created_at          DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_refunds_razorpay_refund_id (razorpay_refund_id),
    KEY idx_refunds_payment (payment_id),
    CONSTRAINT fk_refunds_payment FOREIGN KEY (payment_id) REFERENCES payments(id) ON DELETE RESTRICT
) ENGINE=InnoDB;


-- =====================================================================
-- 9. REVIEWS
-- =====================================================================

-- order_item_id (nullable at the DB level, enforced NOT NULL by app
-- logic before publish) proves the reviewer actually bought the item —
-- "verified purchase" reviews.
CREATE TABLE reviews (
    id              BIGINT AUTO_INCREMENT PRIMARY KEY,
    product_id      BIGINT NOT NULL,
    user_id         BIGINT NOT NULL,
    order_item_id   BIGINT,
    rating          TINYINT NOT NULL CHECK (rating BETWEEN 1 AND 5),
    title           VARCHAR(150),
    body            TEXT,
    is_approved     BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_reviews_user_product (user_id, product_id),
    KEY idx_reviews_product (product_id),
    CONSTRAINT fk_reviews_product FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    CONSTRAINT fk_reviews_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_reviews_order_item FOREIGN KEY (order_item_id) REFERENCES order_items(id) ON DELETE SET NULL
) ENGINE=InnoDB;


-- =====================================================================
-- 10. COMMISSION & VENDOR PAYOUTS (admin reporting)
-- =====================================================================

-- Overrides vendor_profiles.default_commission_rate for a specific
-- vendor+category combination (e.g. platform takes less commission on
-- high-value electronics). Resolution order in application code:
-- commission_rules(vendor+category) -> commission_rules(category, vendor NULL)
-- -> vendor_profiles.default_commission_rate.
CREATE TABLE commission_rules (
    id          BIGINT AUTO_INCREMENT PRIMARY KEY,
    vendor_id   BIGINT,
    category_id BIGINT,
    rate        DECIMAL(5,2) NOT NULL CHECK (rate >= 0 AND rate <= 100),
    created_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_commission_rules_vendor_category (vendor_id, category_id),
    CONSTRAINT fk_commission_rules_vendor FOREIGN KEY (vendor_id) REFERENCES vendor_profiles(id) ON DELETE CASCADE,
    CONSTRAINT fk_commission_rules_category FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Periodic payout batches — what the platform owes each vendor after
-- commission, generated by a scheduled Celery task.
CREATE TABLE vendor_payouts (
    id                  BIGINT AUTO_INCREMENT PRIMARY KEY,
    vendor_id           BIGINT NOT NULL,
    period_start        DATE NOT NULL,
    period_end          DATE NOT NULL,
    gross_amount        DECIMAL(12,2) NOT NULL,
    commission_amount   DECIMAL(12,2) NOT NULL,
    net_amount          DECIMAL(12,2) NOT NULL,
    status              VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'paid', 'failed')),
    paid_at             DATETIME,
    created_at          DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    KEY idx_vendor_payouts_vendor (vendor_id),
    CONSTRAINT chk_payout_period CHECK (period_end >= period_start),
    CONSTRAINT fk_vendor_payouts_vendor FOREIGN KEY (vendor_id) REFERENCES vendor_profiles(id) ON DELETE CASCADE
) ENGINE=InnoDB;
