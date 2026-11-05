-- Run in a fresh shop_practice.db. Contains fictional classroom data.
PRAGMA foreign_keys = ON;
BEGIN;
CREATE TABLE products (
    product_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE CHECK (length(trim(name)) > 0),
    category TEXT NOT NULL,
    price_ugx INTEGER NOT NULL CHECK (price_ugx >= 0),
    stock_qty INTEGER NOT NULL DEFAULT 0 CHECK (stock_qty >= 0)
);
INSERT INTO products (product_id, name, category, price_ugx, stock_qty) VALUES
    (1, 'Rice 5kg', 'Food', 22000, 40),
    (2, 'Sugar 1kg', 'Food', 5500, 120),
    (3, 'Cooking oil 3L', 'Food', 24000, 25),
    (4, 'Bar soap', 'Household', 2500, 200),
    (5, 'Detergent 1kg', 'Household', 9000, 60),
    (6, 'Exercise book', 'Stationery', 1500, 300),
    (7, 'Pen (blue)', 'Stationery', 500, 500),
    (8, 'Phone charger', 'Electronics', 15000, 18),
    (9, 'Earphones', 'Electronics', 12000, 0);
COMMIT;
