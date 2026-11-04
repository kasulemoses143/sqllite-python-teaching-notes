"""Part 11 demo: fresh in-memory data; exports cash_book.csv to the working directory."""
import csv
import sqlite3

conn = sqlite3.connect(":memory:")
conn.row_factory = sqlite3.Row
conn.execute("PRAGMA foreign_keys = ON")

conn.executescript("""
CREATE TABLE IF NOT EXISTS plots (
    plot_id   INTEGER PRIMARY KEY,
    name      TEXT NOT NULL UNIQUE,
    trees     INTEGER NOT NULL CHECK (trees > 0),
    intercrop TEXT                       -- e.g. 'soya beans', or NULL if none
);

CREATE TABLE IF NOT EXISTS harvests (
    harvest_id   INTEGER PRIMARY KEY,
    plot_id      INTEGER NOT NULL REFERENCES plots(plot_id),
    harvested_on TEXT NOT NULL,          -- ISO date: YYYY-MM-DD
    kilos        REAL NOT NULL CHECK (kilos > 0),
    notes        TEXT
);

CREATE TABLE IF NOT EXISTS sales (
    sale_id            INTEGER PRIMARY KEY,
    sold_on            TEXT NOT NULL,
    buyer              TEXT NOT NULL,
    kilos              REAL NOT NULL CHECK (kilos > 0),
    price_per_kilo_ugx INTEGER NOT NULL CHECK (price_per_kilo_ugx > 0)
);

CREATE TABLE IF NOT EXISTS expenses (
    expense_id  INTEGER PRIMARY KEY,
    spent_on    TEXT NOT NULL,
    category    TEXT NOT NULL,           -- labour, fertiliser, transport, tools ...
    description TEXT,
    amount_ugx  INTEGER NOT NULL CHECK (amount_ugx > 0)
);
""")

with conn:
    conn.executemany("INSERT OR IGNORE INTO plots (name, trees, intercrop) VALUES (?, ?, ?)", [
        ("Plot A", 200, "soya beans"),
        ("Plot B", 150, "soya beans"),
        ("Plot C", 100, None),
    ])
    conn.executemany("INSERT INTO harvests (plot_id, harvested_on, kilos) VALUES (?, ?, ?)", [
        (1, "2026-05-12", 310.5), (1, "2026-06-03", 420.0), (1, "2026-10-20", 280.0),
        (2, "2026-05-14", 190.0), (2, "2026-06-05", 260.5), (2, "2026-10-22", 175.0),
        (3, "2026-06-08", 140.0), (3, "2026-10-25", 120.0),
    ])
    conn.executemany("INSERT INTO sales (sold_on, buyer, kilos, price_per_kilo_ugx) VALUES (?, ?, ?, ?)", [
        ("2026-06-20", "Kasese Traders", 800.0, 6500),
        ("2026-10-30", "Masaka Coffee Co-op", 400.0, 7000),
    ])
    conn.executemany("INSERT INTO expenses (spent_on, category, description, amount_ugx) VALUES (?, ?, ?, ?)", [
        ("2026-03-10", "fertiliser", "NPK, 10 bags", 750000),
        ("2026-05-10", "labour", "Picking, 6 workers x 2 days", 360000),
        ("2026-06-02", "labour", "Picking, 8 workers x 2 days", 480000),
        ("2026-06-18", "transport", "Truck to buyer", 200000),
        ("2026-08-15", "tools", "Pruning saws and tarps", 320000),
        ("2026-10-19", "labour", "Picking, 6 workers x 2 days", 360000),
    ])

def show(title, sql, params=()):
    print(f"--- {title} ---")
    rows = conn.execute(sql, params).fetchall()
    for r in rows:
        print(dict(r))
    print()
    return rows

show("Yield per plot", """
    SELECT p.name,
           p.trees,
           ROUND(COALESCE(SUM(h.kilos), 0), 1)               AS total_kilos,
           ROUND(COALESCE(SUM(h.kilos), 0) / p.trees, 2)     AS
kilos_per_tree
    FROM plots p
    LEFT JOIN harvests h ON h.plot_id = p.plot_id
    GROUP BY p.plot_id
    ORDER BY kilos_per_tree DESC
""")

show("Harvest by month", """
    SELECT strftime('%Y-%m', harvested_on) AS month,
           ROUND(SUM(kilos), 1) AS kilos
    FROM harvests
    GROUP BY month
    ORDER BY month
""")

show("Stock in store (kg)", """
    SELECT (SELECT COALESCE(SUM(kilos), 0) FROM harvests)
         - (SELECT COALESCE(SUM(kilos), 0) FROM sales)  AS kilos_in_store
""")

show("Profit", """
    SELECT (SELECT COALESCE(SUM(kilos * price_per_kilo_ugx), 0) FROM sales) AS income_ugx,
           (SELECT COALESCE(SUM(amount_ugx), 0) FROM expenses) AS costs_ugx,
           (SELECT COALESCE(SUM(kilos * price_per_kilo_ugx), 0) FROM sales)
         - (SELECT COALESCE(SUM(amount_ugx), 0) FROM expenses) AS profit_ugx
""")

show("Expenses by category", """
    SELECT category,
           SUM(amount_ugx) AS total_ugx,
           ROUND(100.0 * SUM(amount_ugx) / SUM(SUM(amount_ugx)) OVER (), 1) AS percent_of_costs
    FROM expenses
    GROUP BY category
    ORDER BY total_ugx DESC
""")

ledger_sql = """
    WITH ledger AS (
        SELECT sold_on AS day,
               'Sale to ' || buyer AS item,
               CAST(kilos * price_per_kilo_ugx AS INTEGER) AS amount_ugx
        FROM sales
        UNION ALL
        SELECT spent_on,
               category || ': ' || COALESCE(description, ''),
               -amount_ugx
        FROM expenses
    )
    SELECT day, item, amount_ugx,
           SUM(amount_ugx) OVER (ORDER BY day, item
                                 ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS running_balance_ugx
    FROM ledger
    ORDER BY day, item
"""
show("Cash book", ledger_sql)

def record_harvest(plot_name, harvested_on, kilos, notes=None):
    row = conn.execute("SELECT plot_id FROM plots WHERE name = ?",
(plot_name,)).fetchone()
    if row is None:
        raise ValueError(f"Unknown plot: {plot_name}")
    with conn:
        conn.execute(
            "INSERT INTO harvests (plot_id, harvested_on, kilos, notes) VALUES (?, ?, ?, ?)",
            (row["plot_id"], harvested_on, kilos, notes),
        )

record_harvest("Plot C", "2026-11-03", 95.5, "Late flush")

cur = conn.execute(ledger_sql)
with open("cash_book.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow([c[0] for c in cur.description])
    writer.writerows(cur.fetchall())

conn.close()
