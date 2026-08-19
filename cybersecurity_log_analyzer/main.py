from log_event import LogEvent
from database import DatabaseManager
from log_analyzer import LogAnalyzer

db = DatabaseManager("security.db")
db.create_table()


with open("security.log", "r") as file:
    for line in file:
        parts = line.strip().split("|")
        event = LogEvent(parts[0], parts[1], parts[2], parts[3])

        db.insert_event(event)

events = db.get_events()
analyzer = LogAnalyzer(events)

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