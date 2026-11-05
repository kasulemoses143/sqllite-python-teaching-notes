"""Reusable shop practice connection; no persistent file or third-party packages."""
from pathlib import Path
import sqlite3


def get_connection():
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    setup = Path(__file__).parent / "sql" / "shop_setup.sql"
    conn.executescript(setup.read_text(encoding="utf-8"))
    return conn


def main():
    from contextlib import closing

    with closing(get_connection()) as conn:
        for row in conn.execute(
            "SELECT name, price_ugx, stock_qty FROM products ORDER BY product_id"
        ):
            print(dict(row))
        print("Products:", conn.execute("SELECT COUNT(*) FROM products").fetchone()[0])


if __name__ == "__main__":
    main()
