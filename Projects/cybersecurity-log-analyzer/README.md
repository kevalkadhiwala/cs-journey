# Cybersecurity Log Analyzer

A Python-based cybersecurity monitoring application that analyses
authentication logs, stores security events in SQLite, detects
suspicious login behaviour, calculates risk scores, and exposes the
results through a FastAPI REST API and web dashboard.

## Technologies

- Python
- SQLite
- FastAPI
- SQL
- JavaScript
- HTML/CSS
- Git/GitHub

## Features

- Security log parsing
- SQLite event storage
- Failed login detection
- Suspicious IP detection
- Brute-force detection
- Detection of successful logins following repeated failures
- Targeted username analysis
- Distributed attack detection (one account attacked from many IPs)
- Risk scoring
- Risk-level classification
- REST API
- Security statistics
- Recent event monitoring
- IP, event-type and date-range filtering
- Paginated event browsing
- Web-based security dashboard

## Quick Start

```bash
# 1. Install dependencies (Python 3.10+)
pip install -r requirements.txt

# 2. Load the sample log into SQLite and print a report
python -m app.ingest

# 3. Start the API
uvicorn app.api:app --reload
```

Then open:

- Dashboard: http://127.0.0.1:8000/dashboard
- Interactive API docs: http://127.0.0.1:8000/docs

To analyse a different log file: `python -m app.ingest --log path/to/file.log`

Log format, one event per line:

```text
2026-08-18 09:01:15|192.168.1.99|LOGIN_FAILED|admin
```

Malformed lines are skipped with a warning instead of crashing the import.

## Running the Tests

```bash
python -m pytest
```

The tests cover every detection rule, risk scoring, the database layer,
log ingestion and the API endpoints.

## Project Structure

```text
app/
  config.py        Paths and settings (works from any folder)
  ingest.py        Reads a log file, stores events, prints a report
  log_event.py     Represents a security log event
  database.py      SQLite storage and queries (parameterised SQL)
  log_analyzer.py  Detection rules and risk scoring
  api.py           FastAPI REST API, also serves the dashboard
static/index.html  Web dashboard
data/security.log  Example security log
tests/             pytest test suite
```

## Security Notes

- All SQL queries are parameterised, so filter values cannot inject SQL.
- Log values (usernames, IPs) are attacker-controlled, so the dashboard
  HTML-escapes them before display to prevent cross-site scripting (XSS).
- CORS only allows configured origins (`LOG_ANALYZER_ALLOWED_ORIGINS`),
  and the API is read-only (GET).

## Improvements

- Restructured into an `app/` package so it runs from any folder
- Fixed a stored XSS issue in the dashboard (log values are now escaped)
- Restricted CORS to configured origins, with no credentials and GET only
- Malformed log lines are skipped instead of crashing the import
- The API returns empty results instead of errors before any log is loaded
- The dashboard is served by the API at `/dashboard`
- Added `requirements.txt` and 33 pytest tests

## Security Analysis

The analyzer evaluates suspicious IP addresses using:

- Number of failed login attempts
- Brute-force behaviour
- Number of targeted usernames
- Successful login following repeated failures

It also looks at each account, not just each IP. Attackers often spread
attempts across many IPs so no single IP crosses the limit. An account
with failed logins from 3 or more different IPs within 10 minutes is
flagged as a **distributed attack**.

These factors contribute to a risk score and classification:

- LOW
- MEDIUM
- HIGH

## API Endpoints

| Endpoint | Description |
|---|---|
| `/` | API status |
| `/dashboard` | Web dashboard |
| `/statistics` | Security event statistics |
| `/suspicious-ips` | Suspicious IP analysis |
| `/high-risk` | High-risk IPs |
| `/targeted-accounts` | Accounts attacked from many IPs |
| `/events` | Security events, newest first, with filters and paging |

### Filtering and paging `/events`

| Parameter | Example | Meaning |
|---|---|---|
| `ip_address` | `192.168.1.99` | Only this IP |
| `event_type` | `LOGIN_FAILED` | Only this event type |
| `start` | `2026-08-18` or `2026-08-18 09:00:00` | From this date/time |
| `end` | `2026-08-18` or `2026-08-18 10:00:00` | Up to this date/time (a date alone includes the whole day) |
| `limit` | `10` | Events per page (1-100, default 10) |
| `offset` | `20` | How many events to skip |

```text
/events?event_type=LOGIN_FAILED&start=2026-08-18&limit=5&offset=5
```

The response includes `total` (all matching events), so a client can
work out how many pages there are. Invalid dates return `400`.

## Example

The analyzer can identify behaviour such as:

```text
192.168.1.99
Failed attempts: 4
Targeted usernames: admin, keval
Brute force: True
Success after failures: True
Risk score: 10
Risk level: HIGH
```
