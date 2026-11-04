# Python + SQLite (sqlite3): Complete Teaching Notes

A complete course for students who know Python basics and are learning databases. Adapted from the supplied **81-page PDF**, credited there to **@kamos, 4 November 2026**. All 14 parts, both projects, exercises and solutions, the eight-session teaching plan, cheat sheets and glossary are included.

Examples use school fees in UGX, shop stock and coffee harvests. Read the notes in order; short snippets build on the schema and data in their lesson. Use a fresh database when changing lesson schemas. Not every snippet is a standalone program: some deliberately demonstrate errors or show SQL syntax templates.

## Contents

- [Course overview](TEACHING_NOTES.md#course-overview)
- [Part 1: Databases, SQL and SQLite](TEACHING_NOTES.md#part-1-databases-sql-and-sqlite)
- [Part 2: Connecting, cursors, commit and close](TEACHING_NOTES.md#part-2-connecting-cursors-commit-and-close)
- [Part 3: Creating tables, data types and constraints](TEACHING_NOTES.md#part-3-creating-tables-data-types-and-constraints)
- [Part 4: Inserting data (Create)](TEACHING_NOTES.md#part-4-inserting-data-create)
- [Part 5: Reading data (SELECT)](TEACHING_NOTES.md#part-5-reading-data-select)
- [Part 6: Updating and deleting data](TEACHING_NOTES.md#part-6-updating-and-deleting-data)
- [Part 7: Relationships, foreign keys and JOINs](TEACHING_NOTES.md#part-7-relationships-foreign-keys-and-joins)
- [Part 8: Transactions and error handling](TEACHING_NOTES.md#part-8-transactions-and-error-handling)
- [Part 9: Intermediate and advanced topics](TEACHING_NOTES.md#part-9-intermediate-and-advanced-topics)
- [Part 10: Full project, School Management System](TEACHING_NOTES.md#part-10-full-project-school-management-system)
- [Part 11: Second project, Coffee Farm Harvest Tracker](TEACHING_NOTES.md#part-11-second-project-coffee-farm-harvest-tracker)
- [Part 12: Best practices, common mistakes and debugging](TEACHING_NOTES.md#part-12-best-practices-common-mistakes-and-debugging)
- [Part 13: Exercises with solutions](TEACHING_NOTES.md#part-13-exercises-with-solutions)
- [Part 14: Lesson plan, teaching tips and cheat sheet](TEACHING_NOTES.md#part-14-lesson-plan-teaching-tips-and-cheat-sheet)

## Run the companion examples

Use Python 3.10 or later with the standard-library sqlite3 module. SQLite 3.25 or later runs the core projects and their window-function reports. Later optional features have their own version requirements in Part 14. No pip install is required for the core examples; the pandas section is optional.

```sh
python --version
python -c "import sqlite3; print(sqlite3.sqlite_version)"
python products.py
python school_manager.py
python coffee_farm.py
python -m unittest -v test_examples
```

Use `python3` if that is how Python is installed on your computer. The school menu stores `school.db` beside its script. The product and farm demos use fresh in-memory databases on each run. The farm demo writes `cash_book.csv` to your current working directory. The school CSV export also uses the current working directory; backups go beside the school script.

The school manager registers and searches students, manages courses and enrolments, records payments, reports fee balances and monthly income, exports CSV and backs up data. The farm example prints yield, stock, income, expenses and a running cash book. Its income calculations use REAL kilos and are approximate reporting values; a financial ledger should use a defined integer weight unit and rounding policy.

## Source and corrections

The [original PDF](teaching-notes.pdf) is retained unchanged for comparison. Read [editorial notes](EDITORIAL_NOTES.md) for technical clarifications and the differences between the printed projects and the runnable files. [Validation](VALIDATION.md) records what was checked. No new license has been assigned to the supplied material.

The full course is in [TEACHING_NOTES.md](TEACHING_NOTES.md).
