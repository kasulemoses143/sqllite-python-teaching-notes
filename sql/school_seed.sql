-- Run once after school_schema.sql in a fresh school_practice.db.
-- Fixed dates and IDs make classroom answers repeatable.
BEGIN;
INSERT INTO students (student_id, full_name, email, phone, joined_on) VALUES
    (1, 'Aisha Nakato', 'aisha@example.com', '0771234567', '2026-05-01'),
    (2, 'Brian Okello', 'brian@example.com', '0759876543', '2026-05-01'),
    (3, 'Carol Namubiru', 'carol@example.com', '0701111111', '2026-05-02'),
    (4, 'David Ssemwogerere', NULL, NULL, '2026-05-03');
INSERT INTO courses (course_id, title, fee_ugx) VALUES
    (1, 'Python Basics', 300000),
    (2, 'Web Development', 450000),
    (3, 'Data Analysis', 400000),
    (4, 'Digital Literacy', 100000);
INSERT INTO enrolments (enrolment_id, student_id, course_id, agreed_fee_ugx, enrolled_on) VALUES
    (1, 1, 1, 300000, '2026-05-04'),
    (2, 1, 2, 450000, '2026-05-04'),
    (3, 2, 1, 300000, '2026-05-04'),
    (4, 3, 3, 400000, '2026-05-04');
INSERT INTO payments (payment_id, enrolment_id, amount_ugx, paid_on, method) VALUES
    (1, 1, 100000, '2026-05-05', 'mobile money'),
    (2, 1, 200000, '2026-05-10', 'cash'),
    (3, 2, 200000, '2026-05-10', 'mobile money'),
    (4, 3, 150000, '2026-06-01', 'cash');
COMMIT;
