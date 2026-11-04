# Validation

Checked on 4 November 2026 with Python 3.15.0 and SQLite 3.53.4.

- All 14 numbered parts and 111 numbered subsections match the source section inventory.
- Exercises 1 through 14 are present, with their solutions; the mini-project choices and marking guide remain in Part 13.
- All 99 Python-fenced lesson blocks parse successfully. Seven SQL-fenced blocks are syntax illustrations, including deliberately unsafe examples; they are not Python programs.
- All three runnable companion scripts pass Python syntax checks.
- Five automated tests pass: school schema/constraints, payments/reports, backup/CSV, farm reports/repeatability, product data.
- The transfer teaching example executes and preserves both balances after an unknown-recipient error.
- The farm demo reports 696 kg remaining and UGX 5,530,000 income minus recorded expenses. Repeated runs produce the same results.
- The school chapter code matches its runnable companion program.
- Repository-relative document links resolve.
- The source PDF is unchanged. SHA-256: `46e25ed1465156a2a062f28c29f4e13b074e1a46fb9f02b34dc38a801b39cb20`.

Run the automated checks from the repository root:

```sh
python -m unittest -v test_examples
```

Syntax checks do not execute every lesson fragment. Many fragments depend on prior lesson state, optional packages or external sample files, and some intentionally demonstrate errors. The index timing example was not benchmarked; performance depends on the computer and data. Multiwriter stress testing is outside this teaching package's validation.
