# Teacher guide

The required course is [TEACHING_NOTES.md](TEACHING_NOTES.md). Teach SQL in an editor first; use Python from Unit 7. Keep [SOLUTIONS.md](SOLUTIONS.md) out of view until students have attempted the questions. Optional features should not displace core practice.

## Before the first class

- Create both practice databases using the README instructions. Confirm the row counts.
- Keep the original setup files available so every student can reset to identical data.
- Use fictional records. Do not ask learners to enter real student phone numbers or payment details.
- Check Python availability before Unit 7. Learners need functions, tuples, exceptions, and basic imports at that stage.
- Keep database editor and Python changes coordinated: save or roll back editor transactions before a script writes to the same file.

## Eight sessions of about two hours

Each session: 10 minutes retrieval/prediction, 25 minutes demonstration, 45 minutes guided practice, 30 minutes independent work, 10 minutes explanation and exit question. If learners need more time, split a session; do not fill an unfinished core lesson with extensions.

| Session | Material | Demonstration | Practice / exit question |
| --- | --- | --- | --- |
| 1 | Unit 1, Unit 2 through sorting | Inspect nine products; predict low-stock results | Exercises 1–2. What does one product row mean? |
| 2 | Rest of Unit 2, Unit 3 | Compare parentheses; turn product rows into category totals | Exercises 3–5. Why WHERE versus HAVING? |
| 3 | Unit 4 | Repair a repeated school spreadsheet and draw the relationships | Exercise 6. Where does an agreed fee belong? |
| 4 | Unit 5 | Preview changes, break a constraint, roll back a transaction | Exercises 7–8. What does rollback undo? |
| 5 | Unit 6 through the balance report | Show two payment rows repeating one agreed fee | Trace the intermediate rows. Why does David disappear from an inner join? |
| 6 | Rest of Unit 6; report practice | COUNT(*) versus child-key count; subquery versus joined result | Exercises 9–10. Explain a report without reading its SQL aloud. |
| 7 | Unit 7 | Parameterised search; successful transfer; rollback after a missing receiver | Exercises 11–12. How does Python supply values safely? |
| 8 | Unit 8 and project review | Connect the project functions; change a course price; check a backup | Project demonstration, correctness checks, design explanation |

The independent project needs additional homework time. Complete its schema review after session 6 and build functions after session 7. For students new to Python, add a Python preparation session; do not compress SQL to fit.

## Demonstration habits

Ask for the predicted result before running SQL. Start with tables containing only a few relevant rows. Draw the output of a join before grouping it. Pair students: one writes a query, the other explains which records it keeps; swap roles.

Introduce mistakes intentionally, then identify their causes: missing WHERE, `= NULL`, unmatched foreign key, right-table filtering after LEFT JOIN, and a repeated fee summed after a payment join. Use a disposable database and roll back changes.

A constraint violation in an explicit editor transaction may leave the transaction open. Roll back the experiment before starting another. A setup script error should be resolved before teaching queries against a partially populated database.

## Core success criteria

A student is ready for extensions when they can:

1. State what one row represents in a source table and a report.
2. Write a filtered query and justify its sorting and NULL handling.
3. Explain an aggregate and distinguish WHERE from HAVING.
4. Design a linking table with suitable keys and rules.
5. Preserve unmatched records and avoid accidental double counting.
6. Preview a targeted update and undo a transaction.
7. Pass values safely from Python and explain a rollback after partial work.
8. Compare a report with an expected answer calculated by hand.

Use the 20-mark project rubric in Unit 8. Assess explanations as well as working code. Do not require triggers, window functions, JSON, or a web interface to pass.

## Short recap questions

| Question | Expected idea |
| --- | --- |
| Does zero mean the same as NULL? | No: known none versus missing/unknown. |
| Why not join on names? | Names can repeat or change; keys identify records. |
| Why can Aisha appear twice? | A result row represents an enrolment or payment, not necessarily a student. |
| Can a query run and still be wrong? | Yes: the population, grouping, or repeated values may be wrong. |
| Does `with conn:` close a connection? | No; transaction handling and closing are separate. |
| Why capture the agreed fee? | A later advertised price should not change an earlier agreement. |
| Can direct SQL bypass the project's overpayment check? | Yes; it is enforced by the payment function, not just the positive-amount CHECK. |
| Why test a backup? | A backup is useful only if it can be opened and the required records recovered. |

## Optional next steps

Choose one extension based on the class: coffee farm reporting; course offerings/terms; library physical copies; or shop receipts with stock changes in one transaction. Use [OPTIONAL_TOPICS.md](OPTIONAL_TOPICS.md) as a reference, not a second compulsory syllabus.
