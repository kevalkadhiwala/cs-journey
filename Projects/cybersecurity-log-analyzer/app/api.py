from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from app import config
from app.database import DatabaseManager
from app.log_analyzer import LogAnalyzer

app = FastAPI(title="Cybersecurity Log Analyzer")

# Only the listed origins may call the API from another page.
# No cookies or auth headers are used, so credentials stay disabled,
# and the API is read-only, so only GET is allowed.
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["*"]
)


def get_database():
    # config.DATABASE_PATH is read on every call so tests can point it
    # at a temporary database. create_table() is safe to repeat
    # (CREATE TABLE IF NOT EXISTS) and stops "no such table" errors
    # when the API starts before any log has been ingested.
    db = DatabaseManager(config.DATABASE_PATH)
    db.create_table()
    return db


def get_analyzer():

    db = get_database()

    events = db.get_events()

    return LogAnalyzer(events)

@app.get("/")
def home():
    return {
        "message": "Cybersecurity Log Analyzer API is running!"
    }


@app.get("/dashboard", include_in_schema=False)
def dashboard():
    # Serving the dashboard from the API means it shares the API's
    # origin, so the browser needs no CORS exception at all.
    return FileResponse(config.STATIC_DIR / "index.html")


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

@app.get("/targeted-accounts")
def targeted_accounts():

    analyzer = get_analyzer()

    reports = []

    for username in analyzer.find_targeted_accounts():
        reports.append(analyzer.analyze_account(username))

    return {
        "count": len(reports),
        "targeted_accounts": reports
    }

@app.get("/events")
def get_events(
    ip_address: str | None = Query(default=None),
    event_type: str | None = Query(default=None)
):

    db = get_database()

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

    db = get_database()

    statistics = db.get_event_statistics()

    failed_logins = statistics.get("LOGIN_FAILED", 0)
    successful_logins = statistics.get("LOGIN_SUCCESS", 0)

    total_events = sum(statistics.values())

    events = db.get_events()

    analyzer = LogAnalyzer(events)

    suspicious_ips = analyzer.detect_suspicious_ips()

    targeted_accounts = analyzer.find_targeted_accounts()

    return {
        "total_events": total_events,
        "failed_logins": failed_logins,
        "successful_logins": successful_logins,
        "suspicious_ips": len(suspicious_ips),
        "targeted_accounts": len(targeted_accounts)
    }
