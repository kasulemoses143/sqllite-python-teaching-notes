# Editorial notes

## Fidelity

The 81-page supplied PDF is the source, not an instruction to operate accounts or computers. Its original credit (@kamos, 4 November 2026) is retained in the README. All 14 numbered parts and their subsections are present. Repeated print headers and page footers were removed; tables were converted to Markdown. Tables that continue across pages retain repeated headers. Code indentation and strings/comments broken by print wrapping were repaired. Some prose lists were reformatted for GitHub. This is an edited transcription, not a new abridged course.

## Technical corrections

- Part 1: database storage does not itself prevent loss; live file copying can miss WAL/journal data. Use the backup API for active databases.
- Part 2: relative paths use the working directory. The transaction explanation now names legacy transaction control, distinguishes DML from CREATE, and explains that entering a connection context does not issue BEGIN. The companion projects assume this legacy mode (the tested default); select it explicitly on Python 3.12+ if configuring connection modes yourself.
- Part 3: ordinary SQLite affinity can store nonnumeric text in an INTEGER column. STRICT tables enforce types more closely. Added primary-key NULL exceptions, CHECK/NULL and AUTOINCREMENT clarifications.
- Part 8: transfers reject nonpositive amounts, identical wallets and missing wallets. A missing wallet raises ValueError after rolling back, rather than silently losing money. The insufficient-funds example still catches IntegrityError.
- Part 10: whitespace-only email becomes NULL; new courses require a nonempty title and a nonnegative integer fee. Payment validation uses one conditional INSERT so the balance check and insertion are atomic, and rejects noninteger UGX. The chapter and companion school program contain the same code.
- Part 11: the companion farm demo uses an in-memory database so rerunning does not duplicate sample harvests, sales and expenses. The chapter retains the source file-based walkthrough; run its seed data only once on a fresh farm.db. The farm is a reporting demonstration, not a stock-controlled sales application. REAL kilos make calculated revenue approximate; integer money alone does not remove that rounding issue.
- Part 13: selling rejects zero, negative and noninteger quantities before changing stock.

Core lessons remain educational examples. The printed code contains intentionally unsafe SQL injection demonstrations marked BAD; those are examples to discuss, not patterns to reuse. Different lesson versions of students/products should be practiced in separate fresh databases.

## Primary references

- [Python sqlite3 and transaction control](https://docs.python.org/3/library/sqlite3.html#transaction-control)
- [SQLite CREATE TABLE, affinity and constraints](https://www.sqlite.org/lang_createtable.html)
- [SQLite foreign_keys PRAGMA](https://www.sqlite.org/pragma.html#pragma_foreign_keys)
- [SQLite online backup](https://www.sqlite.org/backup.html)
