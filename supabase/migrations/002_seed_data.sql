-- ============================================================
-- SUPABASE SEED DATA - Initial admin user and categories
-- ============================================================

-- Admin user (password: admin123)
-- bcrypt hash of "admin123"
INSERT INTO "users" (email, username, hashed_password, full_name, role, is_active, is_verified)
VALUES (
    'admin@omnishop.vn',
    'admin',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.bnGKz.pLw8kMOa',
    'Admin',
    'admin',
    TRUE,
    TRUE
) ON CONFLICT (email) DO NOTHING;

-- Test customer
INSERT INTO "users" (email, username, hashed_password, full_name, role, is_active, is_verified)
VALUES (
    'customer@test.com',
    'testuser',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.bnGKz.pLw8kMOa',
    'Test User',
    'customer',
    TRUE,
    TRUE
) ON CONFLICT (email) DO NOTHING;

-- Categories
INSERT INTO "categories" (name, slug, description, sort_order, is_active) VALUES
    ('Điện tử', 'dien-tu', 'Điện thoại, laptop, tablet và phụ kiện công nghệ', 1, TRUE),
    ('Thời trang', 'thoi-trang', 'Quần áo, giày dép, túi xách nam nữ', 2, TRUE),
    ('Làm đẹp', 'lam-dep', 'Mỹ phẩm, chăm sóc da, nước hoa', 3, TRUE),
    ('Nhà cửa', 'nha-cua', 'Đồ gia dụng, nội thất, trang trí', 4, TRUE),
    ('Sức khỏe', 'suc-khoe', 'Thực phẩm chức năng, vitamin, thiết bị y tế', 5, TRUE),
    ('Thể thao', 'the-thao', 'Dụng cụ gym, yoga, bơi lội, đạp xe', 6, TRUE),
    ('Sách', 'sach', 'Sách kinh doanh, tiểu thuyết, sách học tập', 7, TRUE)
ON CONFLICT (slug) DO NOTHING;

-- Brands
INSERT INTO "brands" (name, slug, is_active) VALUES
    ('Apple', 'apple', TRUE),
    ('Samsung', 'samsung', TRUE),
    ('Xiaomi', 'xiaomi', TRUE),
    ('Nike', 'nike', TRUE),
    ('Adidas', 'adidas', TRUE),
    ('The Ordinary', 'the-ordinary', TRUE),
    ('Anker', 'anker', TRUE),
    ('Sony', 'sony', TRUE)
ON CONFLICT (slug) DO NOTHING;

-- Subscription Plans
INSERT INTO "subscription_plans" (name, slug, description, monthly_price, yearly_price, max_products, max_orders, features, is_active, is_featured, sort_order) VALUES
    ('Free', 'free', 'Dành cho người mới bắt đầu', 0, 0, 50, 100, '["basic_store", "5_products"]', TRUE, FALSE, 0),
    ('Starter', 'starter', 'Cho cửa hàng đang phát triển', 9.99, 99.99, 500, 5000, '["custom_domain", "analytics", "coupons"]', TRUE, FALSE, 1),
    ('Professional', 'professional', 'Cho doanh nghiệp lớn', 29.99, 299.99, 5000, 50000, '["api_access", "multi_vendor", "ai_features", "priority_support"]', TRUE, TRUE, 2),
    ('Enterprise', 'enterprise', 'Giải pháp tùy chỉnh cho doanh nghiệp', 99.99, 999.99, -1, -1, '["dedicated_support", "white_label", "custom_integrations", "slate"]', TRUE, FALSE, 3)
ON CONFLICT (slug) DO NOTHING;
