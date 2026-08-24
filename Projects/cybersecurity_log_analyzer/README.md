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
- Risk scoring
- Risk-level classification
- REST API
- Security statistics
- Recent event monitoring
- IP and event-type filtering
- Web-based security dashboard

## Project Structure

- `main.py` - Reads security logs and stores events
- `log_event.py` - Represents security log events
- `database.py` - Handles SQLite database operations
- `log_analyzer.py` - Performs security analysis
- `api.py` - Provides the FastAPI REST API
- `index.html` - Web dashboard
- `security.log` - Example security log

## Security Analysis

The analyzer evaluates suspicious IP addresses using:

- Number of failed login attempts
- Brute-force behaviour
- Number of targeted usernames
- Successful login following repeated failures

These factors contribute to a risk score and classification:

- LOW
- MEDIUM
- HIGH

## API Endpoints

| Endpoint | Description |
|---|---|
| `/` | API status |
| `/statistics` | Security event statistics |
| `/suspicious-ips` | Suspicious IP analysis |
| `/high-risk` | High-risk IPs |
| `/events` | Recent and filtered security events |

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