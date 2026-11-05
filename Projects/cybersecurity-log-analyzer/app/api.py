from datetime import datetime

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from app import config
from app.database import DatabaseManager
from app.incident_report import generate_incident_report
from app.llm import LLMError, get_llm
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

@app.get("/incident-report/{ip_address}")
def incident_report(ip_address: str):
    # Optional AI feature: with LLM_PROVIDER=off (the default), or if the
    # model fails, the report is written by rules instead.
    analyzer = get_analyzer()

    if ip_address not in analyzer.detect_suspicious_ips():
        raise HTTPException(status_code=404,
                            detail=f"{ip_address} is not a suspicious IP")

    try:
        llm = get_llm()
    except LLMError:
        llm = None   # bad settings should not break the endpoint

    return generate_incident_report(analyzer, ip_address, llm).model_dump()


def parse_date_filter(value, name, end_of_day=False):
    # Accepts "YYYY-MM-DD" or "YYYY-MM-DD HH:MM:SS" and returns the
    # timestamp text stored in the database. A date on its own means
    # the start of that day, or the end of it for the "end" filter.
    if value is None:
        return None

    value = value.strip()

    try:
        datetime.strptime(value, config.TIMESTAMP_FORMAT)
        return value
    except ValueError:
        pass

    try:
        datetime.strptime(value, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"{name} must be YYYY-MM-DD or YYYY-MM-DD HH:MM:SS"
        )

    return value + (" 23:59:59" if end_of_day else " 00:00:00")


@app.get("/events")
def get_events(
    ip_address: str | None = Query(default=None),
    event_type: str | None = Query(default=None),
    start: str | None = Query(default=None, description="from this date/time"),
    end: str | None = Query(default=None, description="up to this date/time"),
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0)
):

    start_time = parse_date_filter(start, "start")
    end_time = parse_date_filter(end, "end", end_of_day=True)

    if start_time and end_time and start_time > end_time:
        raise HTTPException(status_code=400, detail="start must be before end")

    db = get_database()

    filters = {
        "ip_address": ip_address,
        "event_type": event_type,
        "start": start_time,
        "end": end_time
    }

    events = db.get_events_filtered(**filters, limit=limit, offset=offset)

    total = db.count_events_filtered(**filters)

    return {
        "count": len(events),
        "total": total,
        "limit": limit,
        "offset": offset,
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
