"""Check data integrity, reports, backup/CSV, and the lesson demos."""
import contextlib
import csv
import importlib.util
import io
from pathlib import Path
import runpy
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('school_manager', ROOT / 'school_manager.py')
school = importlib.util.module_from_spec(spec)
spec.loader.exec_module(school)


class SchoolTests(unittest.TestCase):
    def setUp(self):
        self.conn = school.get_connection(':memory:')
        self.addCleanup(self.conn.close)
        school.init_db(self.conn)
        self.sid = school.add_student(self.conn, "Aisha O'Connor", 'aisha@example.com')
        self.eid = school.enrol(self.conn, self.sid, 1)

    def test_setup_and_constraints(self):
        self.assertEqual(self.conn.execute('PRAGMA foreign_keys').fetchone()[0], 1)
        school.init_db(self.conn)
        self.assertEqual(len(school.list_courses(self.conn)), 3)
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertIsNone(school.enrol(self.conn, self.sid, 1))
            self.assertIsNone(school.enrol(self.conn, 999, 1))
            self.assertIsNone(school.add_student(self.conn, 'Duplicate', 'AISHA@example.com'))
            self.assertIsNone(school.add_course(self.conn, ' ', 20))
            self.assertIsNone(school.add_course(self.conn, 'New course', -20))
        self.assertEqual(len(school.find_students(self.conn, "O'Connor")), 1)
        for name in ['Blank email 1', 'Blank email 2']:
            self.assertIsNotNone(school.add_student(self.conn, name, '  '))

    def test_payments_and_reports(self):
        self.assertEqual(school.get_balance(self.conn, self.eid), 300000)
        with contextlib.redirect_stdout(io.StringIO()):
            for amount in [0, -1, 300001, 1.5, '100', True]:
                self.assertFalse(school.record_payment(self.conn, self.eid, amount))
            self.assertFalse(school.record_payment(self.conn, 999, 100))
        self.assertTrue(school.record_payment(self.conn, self.eid, 100000))
        self.assertEqual(school.get_balance(self.conn, self.eid), 200000)
        self.assertEqual(school.outstanding_balances(self.conn)[0]['balance_ugx'], 200000)
        self.assertEqual(school.student_statement(self.conn, self.sid)[0]['paid_ugx'], 100000)
        self.assertEqual(school.monthly_income(self.conn)[0]['income_ugx'], 100000)
        self.assertTrue(school.record_payment(self.conn, self.eid, 200000))
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertFalse(school.record_payment(self.conn, self.eid, 1))
        self.assertEqual(school.outstanding_balances(self.conn), [])
        self.assertTrue(school.deactivate_student(self.conn, self.sid))
        self.assertEqual(school.find_students(self.conn, 'Aisha'), [])
        self.assertEqual(school.get_balance(self.conn, self.eid), 0)

    def test_exports_and_backup(self):
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td)
            with patch.object(school, 'DB_PATH', dest / 'school.db'):
                backup = school.backup_database(self.conn)
            with contextlib.closing(sqlite3.connect(backup)) as restored:
                self.assertEqual(restored.execute('PRAGMA integrity_check').fetchone()[0], 'ok')
                self.assertEqual(restored.execute('SELECT COUNT(*) FROM enrolments').fetchone()[0], 1)
            school.export_query_to_csv(self.conn, 'SELECT * FROM v_fee_balances', dest / 'fees.csv')
            with (dest / 'fees.csv').open(newline='', encoding='utf-8') as f:
                rows = list(csv.DictReader(f))
            self.assertEqual(rows[0]['balance_ugx'], '300000')


class LessonDemoTests(unittest.TestCase):
    def test_farm_reports_and_repeat_run(self):
        with tempfile.TemporaryDirectory() as td:
            result = subprocess.run([sys.executable, str(ROOT / 'coffee_farm.py')], cwd=td, text=True, capture_output=True, check=True)
            again = subprocess.run([sys.executable, str(ROOT / 'coffee_farm.py')], cwd=td, text=True, capture_output=True, check=True)
            self.assertEqual(result.stdout, again.stdout)
            self.assertIn("'kilos_in_store': 696.0", result.stdout)
            self.assertIn("'profit_ugx': 5530000.0", result.stdout)
            with (Path(td) / 'cash_book.csv').open(newline='', encoding='utf-8') as f:
                rows = list(csv.DictReader(f))
            self.assertEqual(len(rows), 8)
            self.assertEqual(float(rows[-1]['running_balance_ugx']), 5530000)

    def test_products(self):
        with contextlib.redirect_stdout(io.StringIO()) as out:
            runpy.run_path(str(ROOT / 'products.py'))
        self.assertIn('Products: 9', out.getvalue())


if __name__ == '__main__':
    unittest.main()
