# SQL fundamentals with SQLite and Python

Beginner notes for understanding databases, writing useful SQL, and then using SQL safely from Python. Examples use fictional school fees in UGX, shop stock, and coffee harvests.

Adapted from teaching material credited to **@kamos, 4 November 2026**.

## Start here

1. Read [TEACHING_NOTES.md](TEACHING_NOTES.md). Its eight units teach SQL before Python integration.
2. Create the two practice databases using the SQL files below. Setup and reset instructions are in the notes.
3. Attempt the 12 exercises as you reach them. Check [SOLUTIONS.md](SOLUTIONS.md) afterwards.
4. Build the School Manager. Explore [OPTIONAL_TOPICS.md](OPTIONAL_TOPICS.md) when the core is comfortable.

Teachers: [TEACHER_GUIDE.md](TEACHER_GUIDE.md) contains the eight-session plan, demonstrations, and assessment guidance.

## Practice data

Use a SQL editor such as DB Browser for SQLite. Open a new empty database, then execute all statements in the listed files, in order:

| New database | Setup files |
| --- | --- |
| `shop_practice.db` | [sql/shop_setup.sql](sql/shop_setup.sql) |
| `school_practice.db` | [sql/school_schema.sql](sql/school_schema.sql), then [sql/school_seed.sql](sql/school_seed.sql) |

Do not run these against an older `school.db`: these files create fresh classroom databases, not migrations. To reset, close and recreate only the named practice database, then rerun setup. Enable `PRAGMA foreign_keys = ON` on every new connection, before any transaction.

## Python examples

Python 3.10+ and its standard-library `sqlite3` module are sufficient. The optional farm window-function reports require SQLite 3.25+. Check the engine version with `python -c "import sqlite3; print(sqlite3.sqlite_version)"`. Use `python3` if that is your installed command.

From the repository folder:

```sh
python products.py
python school_manager.py
python coffee_farm.py
python verify_course.py
```

| File | Behaviour |
| --- | --- |
| [products.py](products.py) | Prints nine shop records from a fresh in-memory database. Import `get_connection()` to practise queries from Python. |
| [school_manager.py](school_manager.py) | Interactive project; creates `school_project.db` beside the script, with starter courses and no students. Uses the same schema as the lessons. |
| [coffee_farm.py](coffee_farm.py) | Optional reports using a fresh in-memory database; writes `cash_book.csv` in the working directory. |
| [verify_course.py](verify_course.py) | Checks the lesson SQL, expected results, and key project behaviours using temporary databases. |

The School Manager's CSV export goes to the working directory; timestamped backups go beside the script. Practice files and project data remain separate. Existing `school.db` files are not upgraded or opened by this revised project.

For product exercises, save a script in this repository folder:

```python
from contextlib import closing
from products import get_connection

with closing(get_connection()) as conn:
    rows = conn.execute(
        'SELECT name FROM products WHERE name LIKE ? ORDER BY name',
        ('%Cooking%',),
    ).fetchall()
    print([row['name'] for row in rows])
```

Expected: `['Cooking oil 3L']`. Each new helper connection starts fresh. To retain changes between runs, use a file database instead.

## What the school model assumes

One enrolment per student/course pair; whole-shilling payments; no overpayments through the project payment function; deactivation retains financial history. The agreed fee is captured at enrolment, so later advertised fee changes do not rewrite existing balances. Repeat course offerings, refunds, and multi-user deployment are extension work.
