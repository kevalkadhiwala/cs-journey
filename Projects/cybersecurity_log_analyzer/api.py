from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from Projects.cybersecurity_log_analyzer.database import DatabaseManager
from Projects.cybersecurity_log_analyzer.log_analyzer import LogAnalyzer

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

def get_analyzer():

    db = DatabaseManager("security.db")

    events = db.get_events()

    return LogAnalyzer(events)

@app.get("/")
def home():
    return {
        "message": "Cybersecurity Log Analyzer API is running!"
    }


@app.get("/suspicious-ips")
def suspicious_ips():

    analyzer = get_analyzer()

    suspicious = analyzer.detect_suspicious_ips()

    reports = []

    for ip in suspicious:
        report = analyzer.analyze_ip(ip)
        reports.append(report)

    return {"count": len(reports),
            "suspicious_ips": reports}

@app.get("/high-risk")
def high_risk_ips():

    analyzer = get_analyzer()

    suspicious_ips = analyzer.detect_suspicious_ips()

    high_risk = []

    for ip in suspicious_ips:

        report = analyzer.analyze_ip(ip)

        if report["risk_level"] == "HIGH":
            high_risk.append(report)

    return {
        "count": len(high_risk),
        "high_risk_ips": high_risk
    }

@app.get("/events")
def get_events(
    ip_address: str | None = Query(default=None),
    event_type: str | None = Query(default=None)
):

    db = DatabaseManager("security.db")

    if ip_address or event_type:

        events = db.get_events_filtered(
            ip_address=ip_address,
            event_type=event_type
        )

    else:

        events = db.get_recent_events()

    return {
        "count": len(events),
        "events": [
            {
                "timestamp": event.timestamp,
                "ip_address": event.ip_address,
                "event_type": event.event_type,
                "username": event.username
            }
            for event in events
        ]
    }

@app.get("/statistics")
def get_statistics():

    db = DatabaseManager("security.db")

    statistics = db.get_event_statistics()

    failed_logins = statistics.get("LOGIN_FAILED", 0)
    successful_logins = statistics.get("LOGIN_SUCCESS", 0)

    total_events = sum(statistics.values())

    events = db.get_events()

    analyzer = LogAnalyzer(events)

    suspicious_ips = analyzer.detect_suspicious_ips()

    return {
        "total_events": total_events,
        "failed_logins": failed_logins,
        "successful_logins": successful_logins,
        "suspicious_ips": len(suspicious_ips)
    }

