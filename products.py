import sqlite3

conn = sqlite3.connect(":memory:")
cur = conn.cursor()

cur.execute("""
    CREATE TABLE products (
        product_id INTEGER PRIMARY KEY,
        name       TEXT NOT NULL,
        category   TEXT NOT NULL,
        price_ugx  INTEGER NOT NULL,
        stock_qty  INTEGER NOT NULL
    )
""")

products = [
    ("Rice 5kg",        "Food",      22000, 40),
    ("Sugar 1kg",       "Food",       5500, 120),
    ("Cooking oil 3L",  "Food",      24000, 25),
    ("Bar soap",        "Household",  2500, 200),
    ("Detergent 1kg",   "Household",  9000, 60),
    ("Exercise book",   "Stationery", 1500, 300),
    ("Pen (blue)",      "Stationery",  500, 500),
    ("Phone charger",   "Electronics",15000, 18),
    ("Earphones",       "Electronics",12000, 0),
]
cur.executemany(
    "INSERT INTO products (name, category, price_ugx, stock_qty) VALUES (?, ?, ?, ?)",
    products
)
conn.commit()
print("Products:", conn.execute("SELECT COUNT(*) FROM products").fetchone()[0])
conn.close()
