# Exercise solutions

Attempt the questions in [TEACHING_NOTES.md](TEACHING_NOTES.md) first. SQL answers assume untouched setup data. Use `shop_practice.db` for 1–5 and 7; `school_practice.db` for 8–10. Python answers use temporary databases. Equivalent queries can be correct: explain their meaning and check the result.

## 1. Read product records

```sql
SELECT name, category FROM products ORDER BY product_id;
```

Nine rows: one per product. Stock quantities describe each product; they do not create additional rows.

## 2. Filter a price range

```sql
SELECT name, price_ugx
FROM products
WHERE price_ugx BETWEEN 2000 AND 15000
ORDER BY price_ugx, product_id;
```

| name | price_ugx |
| --- | --- |
| Bar soap | 2500 |
| Sugar 1kg | 5500 |
| Detergent 1kg | 9000 |
| Earphones | 12000 |
| Phone charger | 15000 |

Five rows. Both endpoints are included.

## 3. Patterns and parentheses

```sql
SELECT name FROM products WHERE name LIKE '%Cooking%' ORDER BY name;

SELECT name FROM products
WHERE category IN ('Food', 'Household') AND stock_qty < 30
ORDER BY name;
```

Both return Cooking oil 3L. The second query can also use `(category = 'Food' OR category = 'Household') AND stock_qty < 30`. Without parentheses, AND takes priority and would leave all Food products in the result.

## 4. Group and average

```sql
SELECT category, COUNT(*) AS products, ROUND(AVG(price_ugx)) AS average_price_ugx
FROM products
GROUP BY category
ORDER BY category;
```

| category | products | average_price_ugx |
| --- | --- | --- |
| Electronics | 2 | 13500 |
| Food | 3 | 17167 |
| Household | 2 | 5750 |
| Stationery | 2 | 1000 |

This is the average listed product price, not an average weighted by stock quantity.

## 5. Filter group totals

```sql
SELECT category, SUM(price_ugx * stock_qty) AS stock_value_ugx
FROM products
GROUP BY category
HAVING SUM(price_ugx * stock_qty) > 500000
ORDER BY category;
```

Food: 2140000; Household: 1040000; Stationery: 700000. HAVING tests the total after the group exists; WHERE filters individual input rows.

## 6. Design a library

A possible design:

| Table | One row means | Keys and useful rules |
| --- | --- | --- |
| books | One catalogue title/edition | `book_id` primary key; title required |
| members | One registered member | `member_id` primary key; name required |
| loans | One borrowing event | `loan_id` primary key; book/member foreign keys; loan and due dates required; nullable return date |

The return date belongs to the loan: the same book can be returned on different dates in different borrowing events. `NULL` means not yet returned. A physical-copy library would add `book_copies` and loan a particular copy. Make the chosen scope explicit.

Repeated student phone values risk disagreement when only one copy is updated. Store the phone once in `students`, then link enrolments through the student ID.

## 7. Sell three chargers

```sql
SELECT name, stock_qty FROM products WHERE product_id = 8;
BEGIN;
UPDATE products SET stock_qty = stock_qty - 3
WHERE product_id = 8 AND stock_qty >= 3;
SELECT name, stock_qty FROM products WHERE product_id = 8;
ROLLBACK;
```

Stock changes from 18 to 15, then returns to 18 after rollback. The conditional update prevents an oversale; the table's nonnegative CHECK also protects against invalid stock. Python callers should validate a positive whole quantity and inspect `rowcount` to distinguish success from no matching record.

## 8. Preserve an agreed fee

```sql
BEGIN;
UPDATE courses SET fee_ugx = 350000 WHERE course_id = 1;
SELECT c.fee_ugx AS advertised_fee_ugx, e.agreed_fee_ugx,
       b.balance_ugx
FROM enrolments e
JOIN courses c ON c.course_id = e.course_id
JOIN v_fee_balances b ON b.enrolment_id = e.enrolment_id
WHERE e.enrolment_id = 1;
ROLLBACK;
```

Advertised: 350000; agreed: 300000; balance: 0. Aisha has paid her agreed fee. Repricing the catalogue should not rewrite that agreement.

## 9. Include empty courses

```sql
SELECT c.title, COUNT(e.enrolment_id) AS enrolments
FROM courses c
LEFT JOIN enrolments e ON e.course_id = c.course_id
GROUP BY c.course_id, c.title
ORDER BY c.course_id;
```

Python Basics: 2; Web Development: 1; Data Analysis: 1; Digital Literacy: 0. COUNT(*) counts the preserved Digital Literacy result row, even though its child key is NULL. COUNT(e.enrolment_id) counts only actual enrolments.

## 10. Students with no payments

```sql
SELECT s.full_name
FROM students s
LEFT JOIN enrolments e ON e.student_id = s.student_id
LEFT JOIN payments p ON p.enrolment_id = e.enrolment_id
GROUP BY s.student_id, s.full_name
HAVING COUNT(p.payment_id) = 0
ORDER BY s.student_id;
```

Carol Namubiru and David Ssemwogerere. Grouping at student level gives one result row per student, regardless of the number of joined payments. This question includes people with no enrolments; “enrolled students who owe money” is a different population.

## 11. Use safe Python parameters

Save this script beside `products.py`. It uses a fresh in-memory database:

```python
from contextlib import closing
from products import get_connection


def search_products(conn, term):
    return conn.execute(
        'SELECT name FROM products WHERE name LIKE ? ORDER BY name',
        (f'%{term}%',),
    ).fetchall()


with closing(get_connection()) as conn:
    assert [r['name'] for r in search_products(conn, 'Cooking')] == ['Cooking oil 3L']
    with conn:
        conn.execute(
            '''INSERT INTO products (name, category, price_ugx, stock_qty)
               VALUES (?, ?, ?, ?)''',
            ("O'Connor notebook", 'Stationery', 3000, 10),
        )
    assert search_products(conn, "O'Connor")[0]['name'] == "O'Connor notebook"
print('Search and apostrophe checks passed')
```

The SQL text stays fixed. Both search patterns and inserted names are passed as data.

## 12. Roll back a partially completed operation

In Unit 7's transfer script, insert this block after the successful transfer, inside the connection block:

```python
before = conn.execute('SELECT * FROM wallets ORDER BY owner').fetchall()
try:
    transfer(conn, 'Aisha', 'Missing wallet', 10000)
except ValueError:
    pass
else:
    raise AssertionError('Unknown receiver should fail')
after = conn.execute('SELECT * FROM wallets ORDER BY owner').fetchall()
assert before == after
print('Both balances unchanged:', after)
```

The debit succeeds first, then the missing receiver is detected. The exception escapes the transaction block, so rollback must undo an already completed debit. A failure at the first debit does not demonstrate reversal of an earlier successful statement as clearly.
