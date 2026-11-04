# Python + SQLite (sqlite3): Complete Teaching Notes

[Read the complete teaching notes](TEACHING_NOTES.md).

A course for students who know Python basics. It includes 14 parts, exercises with solutions, two projects, an eight-session lesson plan, cheat sheets and a glossary. Examples cover school fees in UGX, shop stock and coffee harvests.

Adapted from the supplied 81-page teaching notes, credited to **@kamos, 4 November 2026**. Code formatting and technical explanations have been corrected where needed.

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

## Runnable examples

| File | What it teaches |
| --- | --- |
| [products.py](products.py) | Create and populate the shop practice data from Part 5. |
| [school_manager.py](school_manager.py) | Run the school management project from Part 10. |
| [coffee_farm.py](coffee_farm.py) | Run the coffee farm reports from Part 11. |

Use Python 3.10 or later with the standard-library sqlite3 module. SQLite 3.25 or later is required for the project window-function reports. Optional newer features list their version requirements in Part 14.

```sh
python products.py
python school_manager.py
python coffee_farm.py
```

Use `python3` if that is how Python is installed on your computer. The school project creates `school.db` beside its script. Its CSV export uses the current working directory, and backups go beside the script. The product and farm demos start with fresh in-memory databases on each run; the farm demo writes `cash_book.csv` in the current working directory.

Short snippets in the notes depend on earlier lesson setup. Practice different lesson schemas in fresh databases. The farm chapter uses a file-based walkthrough; run its sample inserts once on a fresh database. The companion farm script uses memory so rerunning it does not duplicate sample records.
