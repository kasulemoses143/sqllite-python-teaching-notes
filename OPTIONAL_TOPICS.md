# Optional SQL and application topics

Complete the core [teaching notes](TEACHING_NOTES.md) first. These extensions are references and choices for further study, not requirements for the beginner project. Reset practice data before comparing results below.

## 1. Dates and monthly reports

Use `school_practice.db`:

```sql
SELECT strftime('%Y-%m', paid_on) AS month, SUM(amount_ugx) AS income_ugx
FROM payments
GROUP BY strftime('%Y-%m', paid_on)
ORDER BY month;
```

Expected: May 2026 = 500000; June 2026 = 150000. Dates use ISO text. SQLite's `date('now')` and CURRENT_DATE use UTC; `'localtime'` uses the computer's configured zone, not a zone inferred from the student's location. For these local-computer examples, the shared schema uses local dates. A deployed multi-zone application needs an explicit time policy.

For a calendar-month timestamp filter, a half-open range avoids including midnight of the following month:

```sql
SELECT payment_id, amount_ugx FROM payments
WHERE paid_on >= '2026-05-01' AND paid_on < '2026-06-01'
ORDER BY paid_on, payment_id;
```

## 2. CTEs make intermediate results readable

A Common Table Expression names an intermediate result. Here payment totals are calculated before being joined:

```sql
WITH paid AS (
    SELECT enrolment_id, SUM(amount_ugx) AS total_ugx
    FROM payments
    GROUP BY enrolment_id
)
SELECT e.enrolment_id, e.agreed_fee_ugx,
       COALESCE(p.total_ugx, 0) AS paid_ugx
FROM enrolments e
LEFT JOIN paid p ON p.enrolment_id = e.enrolment_id
ORDER BY e.enrolment_id;
```

This is particularly useful when combining totals from separate one-to-many relationships without multiplying their rows.

## 3. Window functions keep detail rows

Requires SQLite 3.25+. Unlike GROUP BY, a window calculation can retain each payment:

```sql
SELECT payment_id, paid_on, amount_ugx,
       SUM(amount_ugx) OVER (
           ORDER BY paid_on, payment_id
           ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
       ) AS running_total_ugx
FROM payments
ORDER BY paid_on, payment_id;
```

Expected running totals: 100000, 300000, 500000, 650000. The unique payment ID resolves date ties. Do not confuse chronological running totals with grouping payments into one row per month.

## 4. Upsert and RETURNING

An upsert handles a chosen uniqueness conflict. In this standalone temporary database, a sensor sends an extra harvest weight for the same plot/day:

```sql
CREATE TABLE daily_totals (
    plot_id INTEGER NOT NULL,
    day TEXT NOT NULL,
    kilos REAL NOT NULL CHECK (kilos > 0),
    PRIMARY KEY (plot_id, day)
);
INSERT INTO daily_totals (plot_id, day, kilos)
VALUES (1, '2026-11-04', 35.5)
ON CONFLICT (plot_id, day) DO UPDATE SET kilos = daily_totals.kilos + excluded.kilos;
SELECT * FROM daily_totals;
```

Upsert requires SQLite 3.24+. Run only the INSERT again: kilos becomes 71.0. This adds an incremental delivery; it is not suitable for retransmitting the same cumulative reading, which would double count it. For a replacement total, assign `excluded.kilos` instead. Real sensors may need a unique event ID to prevent duplicate processing.

Avoid teaching `INSERT OR REPLACE` as an ordinary update: it can delete the conflicting record and insert a new one, affecting related data. `INSERT OR IGNORE` can silently skip some invalid values, so choose conflict handling deliberately.

`RETURNING` (SQLite 3.35+) can return columns from a modification. In the school practice database:

```sql
BEGIN;
INSERT INTO students (full_name) VALUES ('Faith Akello')
RETURNING student_id, joined_on;
ROLLBACK;
```

## 5. A trigger for auditing

A trigger can record changes automatically. In `shop_practice.db`:

```sql
CREATE TABLE price_log (
    log_id INTEGER PRIMARY KEY,
    product_id INTEGER NOT NULL,
    old_price INTEGER NOT NULL,
    new_price INTEGER NOT NULL,
    changed_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TRIGGER trg_price_log
AFTER UPDATE OF price_ugx ON products
WHEN OLD.price_ugx <> NEW.price_ugx
BEGIN
    INSERT INTO price_log (product_id, old_price, new_price)
    VALUES (OLD.product_id, OLD.price_ugx, NEW.price_ugx);
END;
BEGIN;
UPDATE products SET price_ugx = 23000 WHERE product_id = 1;
SELECT product_id, old_price, new_price FROM price_log;
ROLLBACK;
```

Expected log inside the transaction: product 1, old price 22000, new price 23000. Rollback undoes both the update and its audit insert. This records what changed, not who changed it. Prefer explicit transaction logic for a beginner stock-sale operation; introduce hidden trigger behaviour only after learners can trace the explicit version.

## 6. Coffee farm assignment

Run `python coffee_farm.py`. It starts fresh in memory each time, prints reports, and exports a cash book. Inspect its source alongside the report output. It requires SQLite 3.25+ for window functions.

Before the additional late harvest is recorded, the example has 1896 kg harvested and 1200 kg sold: 696 kg in store. Sales total UGX 8,000,000 and listed expenses total UGX 2,470,000, giving a cash surplus of UGX 5,530,000 under the assumptions below.

Model assumptions:

- Harvest and sale weights refer to the same product stage; no drying or processing losses.
- No opening stock, credit sales, unpaid expenses, refunds, or asset depreciation.
- All recorded sales are immediately paid and expenses immediately settled.
- The stock report does not prevent overselling; adding a sale-recording rule is extension work.
- REAL weights multiplied by integer prices can still yield fractional amounts. A real payment system needs an explicit rounding policy and stored charged amounts.

Call the simple difference a **cash surplus**, rather than implying a complete accounting profit calculation. The sample later adds another 95.5 kg harvest after the initial reports; rerunning the stock query then gives 791.5 kg.

Assignment: explain why the stock query uses two independent SUM subqueries rather than joining harvests directly to sales. Add a new plot with no harvest and confirm it appears with zero yield. Compare a result checked by hand before adding another report.

## 7. Topics to postpone until a project needs them

| Topic | When it becomes useful |
| --- | --- |
| STRICT tables (SQLite 3.37+) | Stronger type enforcement; still add business constraints and input validation |
| RIGHT/FULL joins (3.39+) | Special reconciliation questions; master INNER and LEFT first |
| JSON functions | Variable-shaped metadata, after learning ordinary relational columns |
| BLOBs | Small binary attachments; evaluate file storage needs first |
| Python SQL functions | A reusable computation genuinely needed inside a query |
| ATTACH DATABASE | Deliberate cross-database queries or archiving with known schemas |
| pandas | A separate data analysis workflow after SQL fundamentals |
| WAL and concurrency | Applications with concurrent access; still only one SQLite writer at a time |
| Web frameworks / ORM | After learners can explain the underlying schema and SQL |

Do not add a login feature merely to make the database project look complete. If a later course introduces authentication, use a maintained password-hashing library and dedicated guidance, rather than a plain general-purpose hash.

## References

- [SQLite dates](https://www.sqlite.org/lang_datefunc.html)
- [SQLite CTEs](https://www.sqlite.org/lang_with.html)
- [SQLite window functions](https://www.sqlite.org/windowfunctions.html)
- [SQLite upsert](https://www.sqlite.org/lang_upsert.html)
- [SQLite triggers](https://www.sqlite.org/lang_createtrigger.html)
- [SQLite WAL](https://www.sqlite.org/wal.html)
