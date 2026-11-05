"""Run classroom SQL and check reports/project rules using disposable databases."""
import ast
from contextlib import closing, redirect_stdout
import csv
import io
import os
from pathlib import Path
import re
import runpy
import sqlite3
import tempfile
from unittest.mock import patch

import products
import school_manager as school

ROOT = Path(__file__).resolve().parent


def blocks(filename, language):
    return re.findall(r'```' + language + r'\n(.*?)```',
                      (ROOT / filename).read_text(encoding='utf-8'), re.S)


def database(kind):
    conn = sqlite3.connect(':memory:')
    if kind == 'shop':
        conn.executescript((ROOT / 'sql/shop_setup.sql').read_text())
    elif kind == 'school':
        conn.executescript((ROOT / 'sql/school_schema.sql').read_text())
        conn.executescript((ROOT / 'sql/school_seed.sql').read_text())
    return conn


def run_sql(conn, source):
    results, statement = [], ''
    for line in source.splitlines(keepends=True):
        statement += line
        if sqlite3.complete_statement(statement):
            cur = conn.execute(statement)
            if cur.description:
                results.append(cur.fetchall())
            statement = ''
    assert not statement.strip(), f'Incomplete SQL: {statement}'
    return results


def check_sql_lessons():
    contexts = {
        'TEACHING_NOTES.md': ['shop'] * 9 + ['school'] * 11
                             + ['shop', 'school', 'school', 'empty'],
        'SOLUTIONS.md': ['shop'] * 6 + ['school'] * 3,
        'OPTIONAL_TOPICS.md': ['school'] * 4 + ['empty', 'school', 'shop'],
    }
    count = 0
    for filename, kinds in contexts.items():
        snippets = blocks(filename, 'sql')
        assert len(snippets) == len(kinds), (filename, len(snippets), len(kinds))
        for index, (source, kind) in enumerate(zip(snippets, kinds)):
            with closing(database(kind)) as conn:
                results = run_sql(conn, source)
                if filename == 'TEACHING_NOTES.md':
                    if index == 1:
                        assert results[0] == [('Earphones', 0), ('Phone charger', 18),
                                              ('Cooking oil 3L', 25)]
                    elif index == 2:
                        assert len(results[0]) == 3
                        assert results[1] == [('Cooking oil 3L',)]
                    elif index == 5:
                        assert results == [[(9, 4150000)]]
                    elif index == 6:
                        assert results[0] == [('Food', 3, 2140000),
                                              ('Household', 2, 1040000),
                                              ('Stationery', 2, 700000),
                                              ('Electronics', 2, 270000)]
                    elif index == 11:
                        assert results[1][0][-3:] == (100000, 50000, 50000)
                        assert conn.execute('SELECT COUNT(*) FROM enrolments').fetchone()[0] == 4
                    elif index in (15, 21):
                        assert results == [[('David Ssemwogerere',)]]
                    elif index == 17:
                        assert results == [[(1, 300000, 1, 100000), (1, 300000, 2, 200000)]]
                    elif index == 18:
                        assert [r[-2:] for r in results[0]] == [(300000, 0), (200000, 250000),
                                                               (150000, 150000), (0, 400000)]
                    elif index == 19:
                        assert results[0][-1] == ('Digital Literacy', 1, 0)
                    elif index == 22:
                        assert [r[-1] for r in results[0]] == [400000, 250000, 150000]
                elif filename == 'SOLUTIONS.md':
                    if index == 1:
                        assert [r[0] for r in results[0]] == ['Bar soap', 'Sugar 1kg',
                                                             'Detergent 1kg', 'Earphones', 'Phone charger']
                    elif index == 3:
                        assert results[0] == [('Electronics', 2, 13500.0), ('Food', 3, 17167.0),
                                              ('Household', 2, 5750.0), ('Stationery', 2, 1000.0)]
                    elif index == 5:
                        assert results == [[('Phone charger', 18)], [('Phone charger', 15)]]
                        assert conn.execute('SELECT stock_qty FROM products WHERE product_id=8').fetchone()[0] == 18
                    elif index == 6:
                        assert results == [[(350000, 300000, 0)]]
                    elif index == 8:
                        assert results == [[('Carol Namubiru',), ('David Ssemwogerere',)]]
                elif filename == 'OPTIONAL_TOPICS.md':
                    if index == 0:
                        assert results == [[('2026-05', 500000), ('2026-06', 150000)]]
                    elif index == 3:
                        assert [r[-1] for r in results[0]] == [100000, 300000, 500000, 650000]
                    elif index == 4:
                        assert results == [[(1, '2026-11-04', 35.5)]]
                    elif index == 6:
                        assert results == [[(1, 22000, 23000)]]
                        assert conn.execute('SELECT COUNT(*) FROM price_log').fetchone()[0] == 0
                count += 1
    return count


def check_python_examples(temp):
    for name in ['TEACHING_NOTES.md', 'SOLUTIONS.md', 'README.md']:
        for source in blocks(name, 'python'):
            ast.parse(source)
    core = blocks('TEACHING_NOTES.md', 'python')
    # The editor-setup prerequisite for the first Python example.
    with closing(sqlite3.connect(temp / 'school_practice.db')) as conn:
        conn.executescript((ROOT / 'sql/school_schema.sql').read_text())
        conn.executescript((ROOT / 'sql/school_seed.sql').read_text())
    namespace = {'__file__': str(temp / 'lesson.py')}
    exec(core[0], namespace)
    exec(core[3], namespace)  # Standalone transfer, including insufficient funds.
    transfer = namespace['transfer']
    with closing(sqlite3.connect(':memory:')) as conn:
        conn.execute('CREATE TABLE wallets (owner TEXT PRIMARY KEY, balance INTEGER CHECK(balance>=0))')
        with conn:
            conn.executemany('INSERT INTO wallets VALUES (?, ?)', [('Aisha', 50000), ('Brian', 70000)])
        exec(blocks('SOLUTIONS.md', 'python')[1], {'conn': conn, 'transfer': transfer})
    exec(core[4], {})  # Project assertions printed in the notes.
    exec(blocks('SOLUTIONS.md', 'python')[0], {})
    exec(blocks('README.md', 'python')[0], {})
    with closing(products.get_connection()) as conn:
        functions = {'sqlite3': sqlite3}
        exec(core[1], functions)
        assert functions['search_products'](conn, 'Cooking')[0]['name'] == 'Cooking oil 3L'
    with closing(school.get_connection(':memory:')) as conn:
        school.init_db(conn)
        functions = {'sqlite3': sqlite3}
        exec(core[2], functions)
        assert functions['register_student'](conn, "O'Connor", ' oc@example.com ') == 1
        try:
            functions['register_student'](conn, '   ')
        except ValueError:
            pass
        else:
            raise AssertionError('Blank name accepted')
    with closing(school.get_connection(temp / 'school_project.db')) as conn:
        school.init_db(conn)
    exec(core[5], namespace)
    with closing(sqlite3.connect(temp / 'school_project_backup.db')) as backup:
        assert backup.execute('SELECT COUNT(*) FROM courses').fetchone()[0] == 3


def check_project(temp):
    with closing(school.get_connection(':memory:')) as conn:
        school.init_db(conn)
        school.init_db(conn)  # Setup can be rerun without duplicate starter courses.
        assert len(school.list_courses(conn)) == 3
        sid = school.add_student(conn, 'Aisha', 'aisha@example.com')
        assert school.add_student(conn, 'Other', 'AISHA@example.com') is None
        assert school.add_student(conn, '  ') is None
        assert school.enrol(conn, 999, 1) is None
        assert school.enrol(conn, sid, 999) is None
        eid = school.enrol(conn, sid, 1)
        assert school.enrol(conn, sid, 1) is None
        assert school.record_payment(conn, eid, 100000)
        for bad in [0, -1, True, 1.5, 999999]:
            assert not school.record_payment(conn, eid, bad)
        assert not school.record_payment(conn, 999, 1)
        assert school.get_balance(conn, eid) == 200000
        assert len(school.outstanding_balances(conn)) == 1
        with conn:
            conn.execute('UPDATE courses SET fee_ugx=350000 WHERE course_id=1')
        assert school.get_balance(conn, eid) == 200000
        sid2 = school.add_student(conn, 'Brian')
        eid2 = school.enrol(conn, sid2, 1)
        assert school.get_balance(conn, eid2) == 350000
        assert school.deactivate_student(conn, sid)
        assert not school.find_students(conn, 'Aisha')
        assert school.get_balance(conn, eid) == 200000
        school.export_query_to_csv(conn, 'SELECT * FROM v_fee_balances', str(temp / 'fees.csv'))
        with (temp / 'fees.csv').open(newline='') as handle:
            assert len(list(csv.DictReader(handle))) == 2
        with patch.object(school, 'DB_PATH', temp / 'school_project.db'):
            target = school.backup_database(conn)
        with closing(sqlite3.connect(target)) as backup:
            assert backup.execute('SELECT COUNT(*) FROM payments').fetchone()[0] == 1
    # Exercise the menu without creating a project database beside the source.
    connect = school.get_connection
    with patch.object(school, 'get_connection', lambda: connect(':memory:')):
        with patch('builtins.input', side_effect=['3', '0']):
            school.main()


def check_links():
    for path in ROOT.glob('*.md'):
        for target in re.findall(r'\]\(([^)]+)\)', path.read_text()):
            if '://' not in target and not target.startswith('#'):
                assert (path.parent / target.split('#')[0]).exists(), (path.name, target)


def main():
    captured = io.StringIO()
    with tempfile.TemporaryDirectory() as directory:
        temp = Path(directory)
        old = Path.cwd()
        try:
            os.chdir(temp)
            with redirect_stdout(captured):
                count = check_sql_lessons()
                check_python_examples(temp)
                check_project(temp)
                farm = runpy.run_path(str(ROOT / 'coffee_farm.py'))
                with (temp / 'cash_book.csv').open(newline='') as handle:
                    ledger = list(csv.DictReader(handle))
                assert len(ledger) == 8
                assert int(ledger[-1]['running_balance_ugx']) == 5530000
                assert sum(int(r['amount_ugx']) for r in ledger) == 5530000
            check_links()
        finally:
            os.chdir(old)
    print(f'Passed: {count} lesson SQL blocks, Python examples, project rules, farm ledger, and file links.')


if __name__ == '__main__':
    main()
