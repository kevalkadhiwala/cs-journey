"""Read a security log file, store its events in SQLite and print a report.

Run from the project folder:
    python -m app.ingest
    python -m app.ingest --log path/to/other.log
"""
import argparse
import sys
from datetime import datetime

from app.config import DATABASE_PATH, DEFAULT_LOG_PATH, TIMESTAMP_FORMAT
from app.database import DatabaseManager
from app.log_analyzer import LogAnalyzer
from app.log_event import LogEvent


def parse_line(line):
    """Turn one 'timestamp|ip|event_type|username' line into a LogEvent.

    Returns None if the line is malformed, instead of crashing.
    """
    parts = [part.strip() for part in line.strip().split("|")]

    if len(parts) != 4 or not all(parts):
        return None

    try:
        datetime.strptime(parts[0], TIMESTAMP_FORMAT)
    except ValueError:
        return None

    return LogEvent(parts[0], parts[1], parts[2], parts[3])


def ingest_file(db, log_path):
    """Store every valid line of the log file. Returns (read, skipped)."""
    read = 0
    skipped = 0

    with open(log_path, "r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):

            if not line.strip():
                continue

            event = parse_line(line)

            if event is None:
                print(f"Skipping malformed line {line_number}: {line.strip()!r}",
                      file=sys.stderr)
                skipped += 1
                continue

            db.insert_event(event)
            read += 1

    return read, skipped


def print_report(analyzer):
    suspicious_ips = analyzer.detect_suspicious_ips()

    for ip in suspicious_ips:

        report = analyzer.analyze_ip(ip)

        print(f"\nSuspicious IP: {report['ip_address']}")
        print(f"Failed attempts: {report['failed_attempts']}")
        print(f"Targeted usernames: {report['targeted_usernames']}")
        print(f"Brute force: {report['brute_force']}")
        print(f"Success after failures: {report['success_after_failures']}")
        print(f"Risk score: {report['risk_score']}")
        print(f"Risk level: {report['risk_level']}")


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Load a security log into SQLite and report suspicious IPs."
    )
    parser.add_argument("--log", default=DEFAULT_LOG_PATH,
                        help="log file to read (default: data/security.log)")
    parser.add_argument("--db", default=DATABASE_PATH,
                        help="SQLite database file (default: security.db)")
    args = parser.parse_args(argv)

    db = DatabaseManager(args.db)
    db.create_table()

    read, skipped = ingest_file(db, args.log)
    print(f"Read {read} events from {args.log} ({skipped} malformed lines skipped)")

    analyzer = LogAnalyzer(db.get_events())
    print_report(analyzer)


if __name__ == "__main__":
    main()
