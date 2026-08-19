from fastapi import FastAPI, Query
from database import DatabaseManager
from log_analyzer import LogAnalyzer

app = FastAPI()


@app.get("/")
def home():
    return {
        "message": "Cybersecurity Log Analyzer API is running!"
    }


@app.get("/suspicious-ips")
def suspicious_ips():

    db = DatabaseManager("security.db")

    events = db.get_events()

    analyzer = LogAnalyzer(events)

    suspicious = analyzer.detect_suspicious_ips()

    reports = []

    for ip in suspicious:
        report = analyzer.analyze_ip(ip)
        reports.append(report)

    return reports

@app.get("/events")
def get_events(ip_address: str | None = Query(default=None)):

    db = DatabaseManager("security.db")

    if ip_address:
        events = db.get_events_by_ip(ip_address)
    else:
        events = db.get_events()

    return [
        {
            "timestamp": event.timestamp,
            "ip_address": event.ip_address,
            "event_type": event.event_type,
            "username": event.username
        }
        for event in events
    ]