from app.config import DEFAULT_LOG_PATH
from app.database import DatabaseManager
from app.ingest import ingest_file, main, parse_line


def test_parse_valid_line():
    event = parse_line("2026-08-18 09:01:15|192.168.1.99|LOGIN_FAILED|admin\n")
    assert (event.timestamp, event.ip_address, event.event_type, event.username) == (
        "2026-08-18 09:01:15", "192.168.1.99", "LOGIN_FAILED", "admin")


def test_parse_rejects_malformed_lines():
    assert parse_line("not a log line") is None
    assert parse_line("2026-08-18 09:01:15|192.168.1.99|LOGIN_FAILED") is None   # 3 fields
    assert parse_line("2026-08-18 09:01:15|192.168.1.99||admin") is None          # empty field
    assert parse_line("18/08/2026 09:01|192.168.1.99|LOGIN_FAILED|admin") is None  # bad date


def test_ingest_skips_bad_lines_without_crashing(tmp_path):
    log = tmp_path / "mixed.log"
    log.write_text(
        "2026-08-18 09:00:00|10.0.0.1|LOGIN_FAILED|admin\n"
        "garbage line\n"
        "\n"
        "2026-08-18 09:00:05|10.0.0.1|LOGIN_FAILED|admin\n"
    )
    db = DatabaseManager(tmp_path / "t.db")
    db.create_table()
    assert ingest_file(db, log) == (2, 1)
    assert len(db.get_events()) == 2


def test_sample_log_ingests_fully(tmp_path):
    db = DatabaseManager(tmp_path / "t.db")
    db.create_table()
    assert ingest_file(db, DEFAULT_LOG_PATH) == (11, 0)


def test_main_runs_from_any_folder(tmp_path, monkeypatch, capsys):
    # Run from an unrelated folder: paths must not depend on the current directory
    monkeypatch.chdir(tmp_path)
    main(["--db", str(tmp_path / "cli.db")])
    output = capsys.readouterr().out
    assert "Read 11 events" in output
    assert "Suspicious IP: 192.168.1.99" in output
    assert "Risk level: HIGH" in output
