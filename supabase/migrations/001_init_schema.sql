-- ============================================================
-- OMNICHANNEL E-COMMERCE - Supabase PostgreSQL Schema
-- Project: jogjbuoucnbzuoatgwgd
-- ============================================================

-- ============================================================
-- USERS & AUTHENTICATION
-- ============================================================
CREATE TABLE IF NOT EXISTS "users" (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(200),
    phone VARCHAR(20),
    avatar_url VARCHAR(500),
    role VARCHAR(20) DEFAULT 'customer',
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_users_email ON "users"(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON "users"(role);

CREATE TABLE IF NOT EXISTS "addresses" (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES "users"(id) ON DELETE CASCADE,
    label VARCHAR(50) DEFAULT 'home',
    full_name VARCHAR(200) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    address_line1 VARCHAR(300) NOT NULL,
    address_line2 VARCHAR(300),
    city VARCHAR(100) NOT NULL,
    state VARCHAR(100),
    postal_code VARCHAR(20),
    country VARCHAR(100) DEFAULT 'Vietnam',
    is_default BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_addresses_user ON "addresses"(user_id);

CREATE TABLE IF NOT EXISTS "follows" (
    id SERIAL PRIMARY KEY,
    follower_id INTEGER NOT NULL REFERENCES "users"(id) ON DELETE CASCADE,
    following_id INTEGER NOT NULL REFERENCES "users"(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_follows_follower ON "follows"(follower_id);
CREATE INDEX IF NOT EXISTS idx_follows_following ON "follows"(following_id);

-- ============================================================
-- PRODUCTS & CATALOG
-- ============================================================
CREATE TABLE IF NOT EXISTS "categories" (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    slug VARCHAR(200) UNIQUE NOT NULL,
    description TEXT,
    image_url VARCHAR(500),
    parent_id INTEGER REFERENCES "categories"(id),
    sort_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_categories_slug ON "categories"(slug);

CREATE TABLE IF NOT EXISTS "brands" (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    slug VARCHAR(200) UNIQUE NOT NULL,
    logo_url VARCHAR(500),
    description TEXT,
    website VARCHAR(500),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_brands_slug ON "brands"(slug);

CREATE TABLE IF NOT EXISTS "products" (
    id SERIAL PRIMARY KEY,
    sku VARCHAR(100) UNIQUE,
    name VARCHAR(500) NOT NULL,
    slug VARCHAR(500) UNIQUE NOT NULL,
    description TEXT,
    short_description VARCHAR(500),
    price FLOAT NOT NULL DEFAULT 0,
    compare_at_price FLOAT,
    cost_price FLOAT,
    currency VARCHAR(10) DEFAULT 'VND',
    stock_quantity INTEGER DEFAULT 0,
    low_stock_threshold INTEGER DEFAULT 5,
    track_inventory BOOLEAN DEFAULT TRUE,
    images JSONB DEFAULT '[]',
    thumbnail_url VARCHAR(500),
    video_url VARCHAR(500),
    category_id INTEGER REFERENCES "categories"(id),
    brand_id INTEGER REFERENCES "brands"(id),
    vendor_id INTEGER,
    tenant_id INTEGER,
    weight FLOAT,
    dimensions JSONB,
    tags JSONB DEFAULT '[]',
    attributes JSONB DEFAULT '{}',
    variants JSONB DEFAULT '[]',
    meta_title VARCHAR(200),
    meta_description TEXT,
    ai_description TEXT,
    status VARCHAR(20) DEFAULT 'active',
    is_featured BOOLEAN DEFAULT FALSE,
    is_bestseller BOOLEAN DEFAULT FALSE,
    rating FLOAT DEFAULT 0.0,
    review_count INTEGER DEFAULT 0,
    supplier_id INTEGER,
    supplier_url VARCHAR(500),
    sync_status VARCHAR(20) DEFAULT 'manual',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_products_slug ON "products"(slug);
CREATE INDEX IF NOT EXISTS idx_products_category ON "products"(category_id);
CREATE INDEX IF NOT EXISTS idx_products_vendor ON "products"(vendor_id);
CREATE INDEX IF NOT EXISTS idx_products_status ON "products"(status);
CREATE INDEX IF NOT EXISTS idx_products_sku ON "products"(sku);

CREATE TABLE IF NOT EXISTS "reviews" (
    id SERIAL PRIMARY KEY,
    product_id INTEGER NOT NULL REFERENCES "products"(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES "users"(id) ON DELETE CASCADE,
    order_id INTEGER,
    rating INTEGER NOT NULL,
    title VARCHAR(200),
    comment TEXT,
    images JSONB DEFAULT '[]',
    is_verified_purchase BOOLEAN DEFAULT FALSE,
    is_approved BOOLEAN DEFAULT TRUE,
    helpful_count INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_reviews_product ON "reviews"(product_id);

CREATE TABLE IF NOT EXISTS "wishlist_items" (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES "users"(id) ON DELETE CASCADE,
    product_id INTEGER NOT NULL REFERENCES "products"(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_wishlist_user ON "wishlist_items"(user_id);
CREATE INDEX IF NOT EXISTS idx_wishlist_product ON "wishlist_items"(product_id);

CREATE TABLE IF NOT EXISTS "inventory_logs" (
    id SERIAL PRIMARY KEY,
    product_id INTEGER NOT NULL REFERENCES "products"(id) ON DELETE CASCADE,
    change_type VARCHAR(50) NOT NULL,
    quantity_change INTEGER NOT NULL,
    previous_quantity INTEGER NOT NULL,
    new_quantity INTEGER NOT NULL,
    reason VARCHAR(200),
    order_id INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_inventory_logs_product ON "inventory_logs"(product_id);

-- ============================================================
-- ORDERS & PAYMENTS
-- ============================================================
CREATE TABLE IF NOT EXISTS "orders" (
    id SERIAL PRIMARY KEY,
    order_number VARCHAR(50) UNIQUE NOT NULL,
    user_id INTEGER NOT NULL REFERENCES "users"(id),
    tenant_id INTEGER,
    status VARCHAR(30) DEFAULT 'pending',
    fulfillment_status VARCHAR(30) DEFAULT 'unfulfilled',
    payment_status VARCHAR(30) DEFAULT 'pending',
    subtotal FLOAT DEFAULT 0,
    discount_amount FLOAT DEFAULT 0,
    shipping_amount FLOAT DEFAULT 0,
    tax_amount FLOAT DEFAULT 0,
    total FLOAT DEFAULT 0,
    currency VARCHAR(10) DEFAULT 'VND',
    shipping_name VARCHAR(200),
    shipping_phone VARCHAR(20),
    shipping_address TEXT,
    shipping_city VARCHAR(100),
    shipping_postal_code VARCHAR(20),
    shipping_country VARCHAR(100),
    shipping_method VARCHAR(100),
    tracking_number VARCHAR(200),
    tracking_url VARCHAR(500),
    customer_note TEXT,
    internal_note TEXT,
    coupon_code VARCHAR(50),
    coupon_id INTEGER,
    payment_method VARCHAR(50),
    payment_id VARCHAR(200),
    paid_at TIMESTAMPTZ,
    refunded_amount FLOAT DEFAULT 0,
    refund_reason TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    confirmed_at TIMESTAMPTZ,
    shipped_at TIMESTAMPTZ,
    delivered_at TIMESTAMPTZ,
    cancelled_at TIMESTAMPTZ
);
CREATE INDEX IF NOT EXISTS idx_orders_number ON "orders"(order_number);
CREATE INDEX IF NOT EXISTS idx_orders_user ON "orders"(user_id);
CREATE INDEX IF NOT EXISTS idx_orders_status ON "orders"(status);

CREATE TABLE IF NOT EXISTS "order_items" (
    id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES "orders"(id) ON DELETE CASCADE,
    product_id INTEGER NOT NULL REFERENCES "products"(id),
    vendor_id INTEGER,
    name VARCHAR(500) NOT NULL,
    sku VARCHAR(100),
    quantity INTEGER NOT NULL,
    unit_price FLOAT NOT NULL,
    total_price FLOAT NOT NULL,
    vendor_amount FLOAT,
    commission_amount FLOAT,
    commission_rate FLOAT,
    payout_status VARCHAR(30) DEFAULT 'pending',
    attributes JSONB DEFAULT '{}',
    fulfillment_status VARCHAR(30) DEFAULT 'unfulfilled',
    shipped_at TIMESTAMPTZ,
    delivered_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_order_items_order ON "order_items"(order_id);

CREATE TABLE IF NOT EXISTS "payments" (
    id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL UNIQUE REFERENCES "orders"(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES "users"(id),
    amount FLOAT NOT NULL,
    currency VARCHAR(10) DEFAULT 'VND',
    method VARCHAR(50) NOT NULL,
    status VARCHAR(30) DEFAULT 'pending',
    payment_intent_id VARCHAR(200),
    transaction_id VARCHAR(200),
    gateway_response JSONB,
    refunded_amount FLOAT DEFAULT 0,
    refund_reason TEXT,
    refunded_at TIMESTAMPTZ,
    description VARCHAR(500),
    payment_metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS "coupons" (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    type VARCHAR(20) DEFAULT 'percentage',
    value FLOAT NOT NULL,
    min_order_amount FLOAT DEFAULT 0,
    max_discount_amount FLOAT,
    usage_limit INTEGER,
    used_count INTEGER DEFAULT 0,
    per_user_limit INTEGER DEFAULT 1,
    start_date TIMESTAMPTZ,
    end_date TIMESTAMPTZ,
    is_active BOOLEAN DEFAULT TRUE,
    applicable_products JSONB DEFAULT '[]',
    applicable_categories JSONB DEFAULT '[]',
    tenant_id INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_coupons_code ON "coupons"(code);

CREATE TABLE IF NOT EXISTS "shipping_methods" (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    price FLOAT DEFAULT 0,
    estimated_days VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    tenant_id INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- CART
-- ============================================================
CREATE TABLE IF NOT EXISTS "carts" (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE NOT NULL REFERENCES "users"(id) ON DELETE CASCADE,
    session_id VARCHAR(100),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS "cart_items" (
    id SERIAL PRIMARY KEY,
    cart_id INTEGER NOT NULL REFERENCES "carts"(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES "users"(id),
    product_id INTEGER NOT NULL REFERENCES "products"(id),
    quantity INTEGER DEFAULT 1,
    attributes JSONB DEFAULT '{}',
    added_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_cart_items_cart ON "cart_items"(cart_id);
CREATE INDEX IF NOT EXISTS idx_cart_items_user ON "cart_items"(user_id);

-- ============================================================
-- MULTI-VENDOR
-- ============================================================
CREATE TABLE IF NOT EXISTS "vendors" (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE NOT NULL REFERENCES "users"(id) ON DELETE CASCADE,
    store_name VARCHAR(200) NOT NULL,
    store_slug VARCHAR(200) UNIQUE NOT NULL,
    store_description TEXT,
    logo_url VARCHAR(500),
    banner_url VARCHAR(500),
    contact_email VARCHAR(255),
    contact_phone VARCHAR(20),
    address TEXT,
    status VARCHAR(20) DEFAULT 'pending',
    is_verified BOOLEAN DEFAULT FALSE,
    rating FLOAT DEFAULT 0.0,
    review_count INTEGER DEFAULT 0,
    total_sales INTEGER DEFAULT 0,
    total_revenue FLOAT DEFAULT 0,
    commission_rate FLOAT DEFAULT 10.0,
    custom_commission BOOLEAN DEFAULT FALSE,
    payout_method VARCHAR(50),
    payout_email VARCHAR(255),
    payout_info JSONB DEFAULT '{}',
    facebook_url VARCHAR(500),
    instagram_url VARCHAR(500),
    website_url VARCHAR(500),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    approved_at TIMESTAMPTZ
);
CREATE INDEX IF NOT EXISTS idx_vendors_slug ON "vendors"(store_slug);
CREATE INDEX IF NOT EXISTS idx_vendors_user ON "vendors"(user_id);

CREATE TABLE IF NOT EXISTS "vendor_payouts" (
    id SERIAL PRIMARY KEY,
    vendor_id INTEGER NOT NULL REFERENCES "vendors"(id),
    order_id INTEGER,
    period_start TIMESTAMPTZ,
    period_end TIMESTAMPTZ,
    amount FLOAT NOT NULL,
    commission_amount FLOAT DEFAULT 0,
    net_amount FLOAT NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    payment_method VARCHAR(50),
    transaction_id VARCHAR(200),
    paid_at TIMESTAMPTZ,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS "vendor_reviews" (
    id SERIAL PRIMARY KEY,
    vendor_id INTEGER NOT NULL REFERENCES "vendors"(id),
    user_id INTEGER NOT NULL REFERENCES "users"(id),
    order_id INTEGER,
    rating INTEGER NOT NULL,
    comment TEXT,
    is_approved BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- MULTI-TENANT / SAAS
-- ============================================================
CREATE TABLE IF NOT EXISTS "tenants" (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    slug VARCHAR(200) UNIQUE NOT NULL,
    subdomain VARCHAR(100) UNIQUE,
    logo_url VARCHAR(500),
    favicon_url VARCHAR(500),
    primary_color VARCHAR(20) DEFAULT '#6366f1',
    secondary_color VARCHAR(20) DEFAULT '#8b5cf6',
    custom_css TEXT,
    custom_domain VARCHAR(200),
    ssl_enabled BOOLEAN DEFAULT TRUE,
    owner_user_id INTEGER REFERENCES "users"(id),
    plan VARCHAR(50) DEFAULT 'free',
    subscription_status VARCHAR(20) DEFAULT 'active',
    subscription_start TIMESTAMPTZ,
    subscription_end TIMESTAMPTZ,
    max_products INTEGER DEFAULT 100,
    max_storage_mb INTEGER DEFAULT 1000,
    max_orders INTEGER DEFAULT 1000,
    max_vendors INTEGER DEFAULT 1,
    max_customers INTEGER DEFAULT 500,
    current_products INTEGER DEFAULT 0,
    current_storage_mb FLOAT DEFAULT 0,
    current_orders INTEGER DEFAULT 0,
    current_customers INTEGER DEFAULT 0,
    billing_email VARCHAR(255),
    stripe_customer_id VARCHAR(200),
    billing_info JSONB DEFAULT '{}',
    settings JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT TRUE,
    is_public BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_tenants_slug ON "tenants"(slug);

CREATE TABLE IF NOT EXISTS "tenant_users" (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER NOT NULL REFERENCES "tenants"(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES "users"(id) ON DELETE CASCADE,
    role VARCHAR(50) DEFAULT 'member',
    permissions JSONB DEFAULT '[]',
    created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_tenant_users_tenant ON "tenant_users"(tenant_id);
CREATE INDEX IF NOT EXISTS idx_tenant_users_user ON "tenant_users"(user_id);

CREATE TABLE IF NOT EXISTS "subscription_plans" (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    monthly_price FLOAT DEFAULT 0,
    yearly_price FLOAT DEFAULT 0,
    currency VARCHAR(10) DEFAULT 'USD',
    max_products INTEGER DEFAULT 100,
    max_storage_mb INTEGER DEFAULT 1000,
    max_orders INTEGER DEFAULT 1000,
    max_vendors INTEGER DEFAULT 1,
    max_customers INTEGER DEFAULT 500,
    features JSONB DEFAULT '[]',
    is_active BOOLEAN DEFAULT TRUE,
    is_featured BOOLEAN DEFAULT FALSE,
    sort_order INTEGER DEFAULT 0,
    stripe_price_monthly_id VARCHAR(200),
    stripe_price_yearly_id VARCHAR(200),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- SOCIAL COMMERCE
-- ============================================================
CREATE TABLE IF NOT EXISTS "posts" (
    id SERIAL PRIMARY KEY,
    author_id INTEGER NOT NULL REFERENCES "users"(id),
    tenant_id INTEGER,
    type VARCHAR(20) DEFAULT 'post',
    content TEXT NOT NULL,
    media JSONB DEFAULT '[]',
    product_ids JSONB DEFAULT '[]',
    like_count INTEGER DEFAULT 0,
    comment_count INTEGER DEFAULT 0,
    share_count INTEGER DEFAULT 0,
    view_count INTEGER DEFAULT 0,
    is_published BOOLEAN DEFAULT TRUE,
    is_pinned BOOLEAN DEFAULT FALSE,
    is_featured BOOLEAN DEFAULT FALSE,
    hashtags JSONB DEFAULT '[]',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_posts_author ON "posts"(author_id);

CREATE TABLE IF NOT EXISTS "comments" (
    id SERIAL PRIMARY KEY,
    post_id INTEGER NOT NULL REFERENCES "posts"(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES "users"(id),
    parent_id INTEGER REFERENCES "comments"(id),
    content TEXT NOT NULL,
    like_count INTEGER DEFAULT 0,
    is_approved BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_comments_post ON "comments"(post_id);

CREATE TABLE IF NOT EXISTS "post_likes" (
    id SERIAL PRIMARY KEY,
    post_id INTEGER NOT NULL REFERENCES "posts"(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES "users"(id),
    created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_post_likes_post ON "post_likes"(post_id);

CREATE TABLE IF NOT EXISTS "livestreams" (
    id SERIAL PRIMARY KEY,
    host_id INTEGER NOT NULL REFERENCES "users"(id),
    tenant_id INTEGER,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    thumbnail_url VARCHAR(500),
    stream_url VARCHAR(500),
    embed_url VARCHAR(500),
    product_ids JSONB DEFAULT '[]',
    status VARCHAR(20) DEFAULT 'scheduled',
    scheduled_at TIMESTAMPTZ,
    started_at TIMESTAMPTZ,
    ended_at TIMESTAMPTZ,
    viewer_count INTEGER DEFAULT 0,
    peak_viewers INTEGER DEFAULT 0,
    like_count INTEGER DEFAULT 0,
    comment_count INTEGER DEFAULT 0,
    share_count INTEGER DEFAULT 0,
    sales_count INTEGER DEFAULT 0,
    sales_amount FLOAT DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS "influencers" (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE NOT NULL REFERENCES "users"(id) ON DELETE CASCADE,
    tenant_id INTEGER,
    display_name VARCHAR(200),
    bio TEXT,
    avatar_url VARCHAR(500),
    followers_count INTEGER DEFAULT 0,
    following_count INTEGER DEFAULT 0,
    post_count INTEGER DEFAULT 0,
    social_links JSONB DEFAULT '{}',
    total_sales INTEGER DEFAULT 0,
    total_revenue FLOAT DEFAULT 0,
    commission_earned FLOAT DEFAULT 0,
    tier VARCHAR(20) DEFAULT 'bronze',
    is_verified BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS "influencer_commissions" (
    id SERIAL PRIMARY KEY,
    influencer_id INTEGER NOT NULL REFERENCES "influencers"(id),
    order_id INTEGER,
    commission_rate FLOAT DEFAULT 10.0,
    order_amount FLOAT NOT NULL,
    commission_amount FLOAT NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    paid_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- AI ENGINE
-- ============================================================
CREATE TABLE IF NOT EXISTS "ai_sessions" (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES "users"(id),
    session_type VARCHAR(30) DEFAULT 'chatbot',
    session_data JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    ended_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS "ai_messages" (
    id SERIAL PRIMARY KEY,
    session_id INTEGER NOT NULL REFERENCES "ai_sessions"(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    message_metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_ai_messages_session ON "ai_messages"(session_id);

CREATE TABLE IF NOT EXISTS "product_recommendations" (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES "users"(id),
    session_id INTEGER REFERENCES "ai_sessions"(id),
    product_id INTEGER NOT NULL REFERENCES "products"(id),
    recommendation_type VARCHAR(30) DEFAULT 'personalized',
    score FLOAT DEFAULT 0,
    reason VARCHAR(200),
    context JSONB DEFAULT '{}',
    is_clicked BOOLEAN DEFAULT FALSE,
    is_purchased BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS "ai_generated_images" (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES "users"(id),
    product_id INTEGER REFERENCES "products"(id),
    prompt TEXT NOT NULL,
    negative_prompt TEXT,
    style VARCHAR(100),
    size VARCHAR(20) DEFAULT '1024x1024',
    image_url VARCHAR(500),
    seed INTEGER,
    steps INTEGER DEFAULT 30,
    cfg_scale FLOAT DEFAULT 7.5,
    model_name VARCHAR(100),
    status VARCHAR(20) DEFAULT 'pending',
    error_message TEXT,
    credits_used FLOAT DEFAULT 1.0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS "search_queries" (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES "users"(id),
    query VARCHAR(500) NOT NULL,
    results_count INTEGER DEFAULT 0,
    clicked_product_ids JSONB DEFAULT '[]',
    converted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_search_queries_query ON "search_queries"(query);

-- ============================================================
-- DROPSHIPPING
-- ============================================================
CREATE TABLE IF NOT EXISTS "suppliers" (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    slug VARCHAR(200) UNIQUE NOT NULL,
    website VARCHAR(500),
    logo_url VARCHAR(500),
    description TEXT,
    contact_email VARCHAR(255),
    contact_phone VARCHAR(20),
    api_endpoint VARCHAR(500),
    api_key_encrypted VARCHAR(500),
    sync_enabled BOOLEAN DEFAULT FALSE,
    sync_interval_minutes INTEGER DEFAULT 60,
    auto_sync_price BOOLEAN DEFAULT TRUE,
    auto_sync_stock BOOLEAN DEFAULT TRUE,
    auto_sync_images BOOLEAN DEFAULT FALSE,
    avg_lead_time_days FLOAT DEFAULT 7.0,
    reliability_score FLOAT DEFAULT 0,
    total_orders INTEGER DEFAULT 0,
    success_rate FLOAT DEFAULT 0,
    status VARCHAR(20) DEFAULT 'active',
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    last_synced_at TIMESTAMPTZ
);
CREATE INDEX IF NOT EXISTS idx_suppliers_slug ON "suppliers"(slug);

CREATE TABLE IF NOT EXISTS "supplier_sync_logs" (
    id SERIAL PRIMARY KEY,
    supplier_id INTEGER NOT NULL REFERENCES "suppliers"(id),
    product_id INTEGER REFERENCES "products"(id),
    sync_type VARCHAR(20) NOT NULL,
    status VARCHAR(20) DEFAULT 'success',
    items_synced INTEGER DEFAULT 0,
    items_failed INTEGER DEFAULT 0,
    error_message TEXT,
    details JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    duration_ms INTEGER
);

CREATE TABLE IF NOT EXISTS "supplier_mappings" (
    id SERIAL PRIMARY KEY,
    supplier_id INTEGER NOT NULL REFERENCES "suppliers"(id),
    product_id INTEGER NOT NULL REFERENCES "products"(id),
    supplier_product_id VARCHAR(200) NOT NULL,
    supplier_product_url VARCHAR(500),
    supplier_price FLOAT,
    supplier_stock INTEGER,
    markup_type VARCHAR(20) DEFAULT 'percentage',
    markup_value FLOAT DEFAULT 20.0,
    selling_price FLOAT,
    auto_fulfill BOOLEAN DEFAULT FALSE,
    fulfillment_status VARCHAR(20) DEFAULT 'pending',
    last_synced_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_supplier_mappings_product ON "supplier_mappings"(product_id);
CREATE INDEX IF NOT EXISTS idx_supplier_mappings_supplier ON "supplier_mappings"(supplier_id);

CREATE TABLE IF NOT EXISTS "auto_fulfillment_orders" (
    id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES "orders"(id),
    supplier_id INTEGER NOT NULL REFERENCES "suppliers"(id),
    mapping_id INTEGER NOT NULL REFERENCES "supplier_mappings"(id),
    supplier_order_id VARCHAR(200),
    status VARCHAR(20) DEFAULT 'pending',
    tracking_number VARCHAR(200),
    tracking_url VARCHAR(500),
    supplier_cost FLOAT,
    shipping_cost FLOAT DEFAULT 0,
    total_cost FLOAT,
    profit FLOAT,
    submitted_at TIMESTAMPTZ,
    confirmed_at TIMESTAMPTZ,
    shipped_at TIMESTAMPTZ,
    delivered_at TIMESTAMPTZ,
    cancelled_at TIMESTAMPTZ,
    error_message TEXT,
    gateway_response JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_auto_fulfillment_order ON "auto_fulfillment_orders"(order_id);

-- ============================================================
-- MARKETPLACE CREDENTIALS (encrypted storage)
-- ============================================================
CREATE TABLE IF NOT EXISTS "marketplace_credentials" (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES "users"(id) ON DELETE CASCADE,
    platform VARCHAR(50) NOT NULL,  -- shopee, lazada, tiktok, facebook, sendo
    credentials_encrypted JSONB NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    last_synced_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_marketplace_credentials_user ON "marketplace_credentials"(user_id);
CREATE INDEX IF NOT EXISTS idx_marketplace_credentials_platform ON "marketplace_credentials"(platform);

-- ============================================================
-- TRIGGERS for updated_at
-- ============================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON "users" FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_products_updated_at BEFORE UPDATE ON "products" FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_orders_updated_at BEFORE UPDATE ON "orders" FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_carts_updated_at BEFORE UPDATE ON "carts" FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_tenants_updated_at BEFORE UPDATE ON "tenants" FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_suppliers_updated_at BEFORE UPDATE ON "suppliers" FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_ai_sessions_updated_at BEFORE UPDATE ON "ai_sessions" FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_auto_fulfillment_updated_at BEFORE UPDATE ON "auto_fulfillment_orders" FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================
-- ROW LEVEL SECURITY (RLS)
-- ============================================================
ALTER TABLE "users" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "addresses" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "products" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "orders" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "cart_items" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "carts" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "wishlist_items" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "reviews" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "marketplace_credentials" ENABLE ROW LEVEL SECURITY;

-- Users: users see own data, admins see all
CREATE POLICY "Users view own" ON "users" FOR SELECT USING (auth.uid() = id);
CREATE POLICY "Users update own" ON "users" FOR UPDATE USING (auth.uid() = id);

-- Products: all can read active products
CREATE POLICY "Products all read" ON "products" FOR SELECT USING (status = 'active' OR true);

-- Orders: users see own, admins see all
CREATE POLICY "Orders view own" ON "orders" FOR SELECT USING (auth.uid() = user_id);

-- Marketplace credentials: admin only
CREATE POLICY "Marketplace credentials admin only" ON "marketplace_credentials" FOR ALL USING (
    EXISTS (SELECT 1 FROM "users" WHERE id = auth.uid() AND role = 'admin')
);
