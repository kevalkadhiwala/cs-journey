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

    def load_all(self):
        with closing(self.connect()) as connection, connection:
            connection.row_factory = sqlite3.Row
            rows = connection.execute(
                "SELECT * FROM students ORDER BY name"
            ).fetchall()

        return [dict(row) for row in rows]
