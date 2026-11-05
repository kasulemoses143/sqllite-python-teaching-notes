-- Shared by the SQL lessons and school_manager.py.
-- IF NOT EXISTS allows setup on an unchanged schema; it is not a migration.
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS students (
    student_id INTEGER PRIMARY KEY,
    full_name TEXT NOT NULL CHECK (length(trim(full_name)) > 0),
    email TEXT UNIQUE,
    phone TEXT,
    joined_on TEXT NOT NULL DEFAULT (date('now', 'localtime')),
    is_active INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1))
);
CREATE TABLE IF NOT EXISTS courses (
    course_id INTEGER PRIMARY KEY,
    title TEXT NOT NULL UNIQUE CHECK (length(trim(title)) > 0),
    fee_ugx INTEGER NOT NULL CHECK (fee_ugx >= 0)
);
CREATE TABLE IF NOT EXISTS enrolments (
    enrolment_id INTEGER PRIMARY KEY,
    student_id INTEGER NOT NULL REFERENCES students(student_id),
    course_id INTEGER NOT NULL REFERENCES courses(course_id),
    agreed_fee_ugx INTEGER NOT NULL CHECK (agreed_fee_ugx >= 0),
    enrolled_on TEXT NOT NULL DEFAULT (date('now', 'localtime')),
    UNIQUE (student_id, course_id)
);
CREATE TABLE IF NOT EXISTS payments (
    payment_id INTEGER PRIMARY KEY,
    enrolment_id INTEGER NOT NULL REFERENCES enrolments(enrolment_id),
    amount_ugx INTEGER NOT NULL CHECK (amount_ugx > 0),
    paid_on TEXT NOT NULL DEFAULT (date('now', 'localtime')),
    method TEXT NOT NULL DEFAULT 'cash'
);
-- UNIQUE(student_id, course_id) already supports lookups by student_id.
CREATE INDEX IF NOT EXISTS idx_enrolments_course ON enrolments(course_id);
CREATE INDEX IF NOT EXISTS idx_payments_enrolment ON payments(enrolment_id);
CREATE VIEW IF NOT EXISTS v_fee_balances AS
SELECT e.enrolment_id, s.student_id, s.full_name, s.phone, c.title,
       e.agreed_fee_ugx AS fee_ugx,
       COALESCE(SUM(p.amount_ugx), 0) AS paid_ugx,
       e.agreed_fee_ugx - COALESCE(SUM(p.amount_ugx), 0) AS balance_ugx
FROM enrolments e
JOIN students s ON s.student_id = e.student_id
JOIN courses c ON c.course_id = e.course_id
LEFT JOIN payments p ON p.enrolment_id = e.enrolment_id
GROUP BY e.enrolment_id, s.student_id, s.full_name, s.phone,
         c.title, e.agreed_fee_ugx;
