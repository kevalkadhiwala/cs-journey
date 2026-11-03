import pytest

from app.database import DatabaseManager
from app.log_event import LogEvent


def make_events(rows):
    return [LogEvent(*row) for row in rows]


# Same scenario as data/security.log
SAMPLE_ROWS = [
    ("2026-08-18 09:00:01", "192.168.1.50", "LOGIN_SUCCESS", "keval"),
    ("2026-08-18 09:01:15", "192.168.1.99", "LOGIN_FAILED", "admin"),
    ("2026-08-18 09:01:18", "192.168.1.99", "LOGIN_FAILED", "admin"),
    ("2026-08-18 09:01:21", "192.168.1.99", "LOGIN_FAILED", "admin"),
    ("2026-08-18 09:01:25", "192.168.1.99", "LOGIN_FAILED", "keval"),
    ("2026-08-18 09:01:29", "192.168.1.99", "LOGIN_SUCCESS", "admin"),
    ("2026-08-18 09:10:00", "192.168.1.77", "LOGIN_FAILED", "unknown"),
    ("2026-08-18 09:45:00", "192.168.1.77", "LOGIN_FAILED", "unknown"),
    ("2026-08-18 10:30:00", "192.168.1.77", "LOGIN_FAILED", "unknown"),
    ("2026-08-18 11:00:00", "192.168.1.50", "LOGIN_SUCCESS", "keval"),
    ("2026-08-18 11:15:00", "192.168.1.50", "LOGOUT", "keval"),
]


@pytest.fixture
def sample_events():
    return make_events(SAMPLE_ROWS)


@pytest.fixture
def db(tmp_path):
    """A fresh SQLite database in a temporary folder for each test."""
    database = DatabaseManager(tmp_path / "test.db")
    database.create_table()
    return database


@pytest.fixture
def loaded_db(db, sample_events):
    for event in sample_events:
        db.insert_event(event)
    return db
