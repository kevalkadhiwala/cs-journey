import sqlite3
from contextlib import closing

# ============================================================
# DATABASE
# ============================================================

# One table holds both student types. The type-specific columns
# (programming_language, specialisation) are NULL when they don't apply.
# NUMERIC keeps whole marks as integers and decimal marks as decimals.
CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS students (
    name                 TEXT PRIMARY KEY,
    mark                 NUMERIC NOT NULL,
    age                  INTEGER NOT NULL,
    student_type         TEXT NOT NULL,
    course_name          TEXT NOT NULL,
    course_code          TEXT NOT NULL,
    programming_language TEXT,
    specialisation       TEXT
)
"""

# One row per student, subject and term, e.g. ("Aisha", "Databases", "2026-S1", 74).
# Each student has at most one mark per subject per term.
CREATE_RESULTS_SQL = """
CREATE TABLE IF NOT EXISTS subject_marks (
    student_name TEXT NOT NULL,
    subject      TEXT NOT NULL,
    term         TEXT NOT NULL,
    mark         NUMERIC NOT NULL CHECK (mark BETWEEN 0 AND 100),
    PRIMARY KEY (student_name, subject, term)
)
"""

COLUMNS = ["name", "mark", "age", "student_type", "course_name",
           "course_code", "programming_language", "specialisation"]


class StudentDatabase:

    def __init__(self, database_name):
        self.database_name = database_name
        self.create_table()

    def connect(self):
        return sqlite3.connect(self.database_name)

    def create_table(self):
        # closing() shuts the connection; the inner "with" commits the changes
        with closing(self.connect()) as connection, connection:
            connection.execute(CREATE_TABLE_SQL)
            connection.execute(CREATE_RESULTS_SQL)

    def save_all(self, student_dicts):
        # Replace every row in one transaction, so a crash halfway
        # through can never leave a half-saved database.
        placeholders = ", ".join("?" for _ in COLUMNS)

        rows = []
        for data in student_dicts:
            rows.append(tuple(data.get(column) for column in COLUMNS))

        with closing(self.connect()) as connection, connection:
            connection.execute("DELETE FROM students")
            connection.executemany(
                f"INSERT INTO students ({', '.join(COLUMNS)}) "
                f"VALUES ({placeholders})",
                rows
            )
            # Results of students who were removed go with them
            connection.execute(
                "DELETE FROM subject_marks "
                "WHERE student_name NOT IN (SELECT name FROM students)"
            )

    def load_all(self):
        with closing(self.connect()) as connection, connection:
            connection.row_factory = sqlite3.Row
            rows = connection.execute(
                "SELECT * FROM students ORDER BY name"
            ).fetchall()

        return [dict(row) for row in rows]

    # ---------------- subject results ----------------

    def set_subject_mark(self, name, subject, term, mark):
        # Adding a mark for the same subject and term again replaces it
        with closing(self.connect()) as connection, connection:
            connection.execute(
                "INSERT INTO subject_marks (student_name, subject, term, mark) "
                "VALUES (?, ?, ?, ?) "
                "ON CONFLICT (student_name, subject, term) "
                "DO UPDATE SET mark = excluded.mark",
                (name, subject, term, mark)
            )

    def get_subject_marks(self, name):
        with closing(self.connect()) as connection, connection:
            connection.row_factory = sqlite3.Row
            rows = connection.execute(
                "SELECT subject, term, mark FROM subject_marks "
                "WHERE student_name = ? ORDER BY term, subject",
                (name,)
            ).fetchall()

        return [dict(row) for row in rows]

    def subject_average(self, subject, term=None):
        # Returns (average, number_of_marks); average is None with no marks
        sql = "SELECT AVG(mark), COUNT(*) FROM subject_marks WHERE subject = ?"
        values = [subject]

        if term:
            sql += " AND term = ?"
            values.append(term)

        with closing(self.connect()) as connection, connection:
            average, count = connection.execute(sql, values).fetchone()

        return (round(average, 1) if average is not None else None), count

    def students_below(self, subject, mark, term=None):
        sql = ("SELECT student_name, term, mark FROM subject_marks "
               "WHERE subject = ? AND mark < ?")
        values = [subject, mark]

        if term:
            sql += " AND term = ?"
            values.append(term)

        sql += " ORDER BY mark, student_name"

        with closing(self.connect()) as connection, connection:
            connection.row_factory = sqlite3.Row
            rows = connection.execute(sql, values).fetchall()

        return [dict(row) for row in rows]

    def list_subjects(self):
        with closing(self.connect()) as connection, connection:
            rows = connection.execute(
                "SELECT DISTINCT subject FROM subject_marks ORDER BY subject"
            ).fetchall()

        return [row[0] for row in rows]
