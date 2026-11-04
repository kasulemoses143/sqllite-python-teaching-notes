"""school_manager.py - a small school management system (Python + SQLite)."""
import csv
import sqlite3
from contextlib import closing
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent / "school.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS students (
    student_id INTEGER PRIMARY KEY,
    full_name  TEXT NOT NULL,
    email      TEXT UNIQUE,
    phone      TEXT,
    joined_on  TEXT NOT NULL DEFAULT (date('now', 'localtime')),
    is_active  INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1))
);

CREATE TABLE IF NOT EXISTS courses (
    course_id INTEGER PRIMARY KEY,
    title     TEXT NOT NULL UNIQUE,
    fee_ugx   INTEGER NOT NULL CHECK (fee_ugx >= 0)
);

CREATE TABLE IF NOT EXISTS enrolments (
    enrolment_id INTEGER PRIMARY KEY,
    student_id   INTEGER NOT NULL,
    course_id    INTEGER NOT NULL,
    enrolled_on  TEXT NOT NULL DEFAULT (date('now', 'localtime')),
    UNIQUE (student_id, course_id),
    FOREIGN KEY (student_id) REFERENCES students(student_id),
    FOREIGN KEY (course_id)  REFERENCES courses(course_id)
);

CREATE TABLE IF NOT EXISTS payments (
    payment_id   INTEGER PRIMARY KEY,
    enrolment_id INTEGER NOT NULL,
    amount_ugx   INTEGER NOT NULL CHECK (amount_ugx > 0),
    paid_on      TEXT NOT NULL DEFAULT (date('now', 'localtime')),
    method       TEXT NOT NULL DEFAULT 'cash',
    FOREIGN KEY (enrolment_id) REFERENCES enrolments(enrolment_id)
);

CREATE INDEX IF NOT EXISTS idx_enrolments_student ON enrolments(student_id);
CREATE INDEX IF NOT EXISTS idx_payments_enrolment ON payments(enrolment_id);

CREATE VIEW IF NOT EXISTS v_fee_balances AS
SELECT e.enrolment_id,
       s.student_id,
       s.full_name,
       s.phone,
       c.title,
       c.fee_ugx,
       COALESCE(SUM(p.amount_ugx), 0)              AS paid_ugx,
       c.fee_ugx - COALESCE(SUM(p.amount_ugx), 0)  AS balance_ugx
FROM enrolments e
JOIN students s ON s.student_id = e.student_id
JOIN courses  c ON c.course_id  = e.course_id
LEFT JOIN payments p ON p.enrolment_id = e.enrolment_id
GROUP BY e.enrolment_id;
"""

STARTER_COURSES = [
    ("Python Basics", 300000),
    ("Web Development", 450000),
    ("Data Analysis", 400000),
]
# ---------- connection and setup ----------

def get_connection(path=DB_PATH):
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db(conn):
    conn.executescript(SCHEMA)
    with conn:
        conn.executemany(
            "INSERT OR IGNORE INTO courses (title, fee_ugx) VALUES (?, ?)", STARTER_COURSES
        )

# ---------- students ----------

def add_student(conn, full_name, email=None, phone=None):
    """Returns the new student_id, or None if it could not be added."""
    full_name = full_name.strip()
    if not full_name:
        print("Name is required.")
        return None
    email = (email.strip().lower() or None) if email else None    # empty email becomes NULL
    try:
        with conn:
            cur = conn.execute(
                "INSERT INTO students (full_name, email, phone) VALUES (?, ?, ?)",
                (full_name, email, phone or None),
            )
            return cur.lastrowid
    except sqlite3.IntegrityError as e:
        print("Could not add student:", "that email is already used." if "UNIQUE" in str(e) else e)
        return None
def find_students(conn, term):
    pattern = f"%{term}%"
    return conn.execute(
        """SELECT student_id, full_name, email, phone, joined_on
           FROM students
           WHERE is_active = 1
             AND (full_name LIKE ? OR email LIKE ? OR phone LIKE ?)
           ORDER BY full_name""",
        (pattern, pattern, pattern),
    ).fetchall()

def deactivate_student(conn, student_id):
    with conn:
        cur = conn.execute(
            "UPDATE students SET is_active = 0 WHERE student_id = ? AND is_active = 1", (student_id,)
        )
    return cur.rowcount == 1

# ---------- courses and enrolment ----------

def list_courses(conn):
    return conn.execute(
        """SELECT c.course_id, c.title, c.fee_ugx, COUNT(e.enrolment_id) AS students
           FROM courses c LEFT JOIN enrolments e ON e.course_id = c.course_id
           GROUP BY c.course_id ORDER BY c.title"""
    ).fetchall()

def add_course(conn, title, fee_ugx):
    if not title.strip() or type(fee_ugx) is not int or fee_ugx < 0:
        print("A course needs a title and a non-negative whole-shilling fee.")
        return None
    try:
        with conn:
            cur = conn.execute("INSERT INTO courses (title, fee_ugx) VALUES (?, ?)", (title.strip(), fee_ugx))
            return cur.lastrowid
    except sqlite3.IntegrityError as e:
        print("Could not add course:", e)
        return None
def enrol(conn, student_id, course_id):
    try:
        with conn:
            cur = conn.execute(
                "INSERT INTO enrolments (student_id, course_id) VALUES (?, ?)", (student_id, course_id)
            )
            return cur.lastrowid
    except sqlite3.IntegrityError as e:
        if "UNIQUE" in str(e):
            print("This student is already enrolled in that course.")
        else:
            print("Unknown student or course ID.")
        return None

# ---------- payments ----------

def get_balance(conn, enrolment_id):
    row = conn.execute(
        "SELECT balance_ugx FROM v_fee_balances WHERE enrolment_id = ?",
(enrolment_id,)
    ).fetchone()
    return None if row is None else row["balance_ugx"]

def record_payment(conn, enrolment_id, amount_ugx, method="cash"):
    if type(amount_ugx) is not int or amount_ugx <= 0:
        print("Payment must be a positive whole number of UGX.")
        return False
    # One statement checks the current balance and inserts the payment atomically.
    with conn:
        cur = conn.execute(
            """INSERT INTO payments (enrolment_id, amount_ugx, method)
               SELECT enrolment_id, ?, ? FROM v_fee_balances
               WHERE enrolment_id = ? AND balance_ugx >= ?""",
            (amount_ugx, method, enrolment_id, amount_ugx),
        )
    if cur.rowcount != 1:
        print("Unknown enrolment or payment exceeds the remaining balance.")
        return False
    return True

# ---------- reports ----------

def outstanding_balances(conn):
    return conn.execute(
        "SELECT * FROM v_fee_balances WHERE balance_ugx > 0 ORDER BY balance_ugx DESC"
    ).fetchall()

def student_statement(conn, student_id):
    return conn.execute(
        "SELECT enrolment_id, title, fee_ugx, paid_ugx, balance_ugx FROM v_fee_balances WHERE student_id = ?",
        (student_id,),
    ).fetchall()

def monthly_income(conn):
    return conn.execute(
        """SELECT strftime('%Y-%m', paid_on) AS month, SUM(amount_ugx) AS income_ugx
           FROM payments GROUP BY month ORDER BY month DESC"""
    ).fetchall()

def export_query_to_csv(conn, sql, filename):
    cur = conn.execute(sql)
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([col[0] for col in cur.description])
        writer.writerows(cur.fetchall())

def backup_database(conn):
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    target = DB_PATH.with_name(f"school_backup_{stamp}.db")
    with closing(sqlite3.connect(target)) as dst:
        conn.backup(dst)
    return target

# ---------- text menu ----------
MENU = """
===== SCHOOL MANAGER =====
1. Register student        6. Record payment
2. Search students         7. Outstanding fees report
3. List courses            8. Student statement
4. Add course              9. Monthly income
5. Enrol student in course 10. Export fees to CSV
11. Deactivate student     12. Backup database
0. Quit
"""

def ask_int(prompt):
    try:
        return int(input(prompt).strip().replace(",", ""))
    except ValueError:
        print("Please type a whole number.")
        return None

def show_rows(rows, columns):
    if not rows:
        print("(nothing found)")
    for r in rows:
        print(" | ".join(str(r[c]) for c in columns))

def main():
    with closing(get_connection()) as conn:
        init_db(conn)
        while True:
            print(MENU)
            choice = input("Choose: ").strip()

            if choice == "1":
                sid = add_student(conn, input("Full name: "), input("Email (optional): "), input("Phone: "))
                if sid:
                    print("Student registered with ID", sid)
            elif choice == "2":
                show_rows(find_students(conn, input("Search (name, email or phone): ")),
                          ["student_id", "full_name", "email", "phone"])
            elif choice == "3":
                for c in list_courses(conn):
                    print(f"{c['course_id']}. {c['title']:<18} UGX {c['fee_ugx']:>9,}  ({c['students']} students)")
            elif choice == "4":
                fee = ask_int("Fee in UGX: ")
                if fee is not None:
                    add_course(conn, input("Course title: "), fee)
            elif choice == "5":
                sid, cid = ask_int("Student ID: "), ask_int("Course ID: ")
                if sid and cid and enrol(conn, sid, cid):
                    print("Enrolled.")
            elif choice == "6":
                eid, amount = ask_int("Enrolment ID: "), ask_int("Amount (UGX): ")
                if eid and amount and record_payment(conn, eid, amount, input("Method (cash/mobile money): ") or "cash"):
                    print("Payment recorded.")
            elif choice == "7":
                for r in outstanding_balances(conn):
                    print(f"{r['full_name']:<20}{r['title']:<18}owes UGX {r['balance_ugx']:>9,}  ({r['phone'] or 'no phone'})")
            elif choice == "8":
                sid = ask_int("Student ID: ")
                for r in (student_statement(conn, sid) if sid else []):
                    print(f"[{r['enrolment_id']}] {r['title']:<18} fee {r['fee_ugx']:>9,}  paid {r['paid_ugx']:>9,}  balance {r['balance_ugx']:>9,}")
            elif choice == "9":
                for r in monthly_income(conn):
                    print(f"{r['month']}  UGX {r['income_ugx']:>11,}")
            elif choice == "10":
                export_query_to_csv(conn, "SELECT * FROM v_fee_balances", "fee_balances.csv")
                print("Saved fee_balances.csv")
            elif choice == "11":
                sid = ask_int("Student ID: ")
                print("Done." if sid and deactivate_student(conn, sid) else "No active student with that ID.")
            elif choice == "12":
                print("Backup saved to", backup_database(conn))
            elif choice == "0":
                print("Goodbye!")
                break
            else:
                print("Invalid choice.")

if __name__ == "__main__":
    main()
