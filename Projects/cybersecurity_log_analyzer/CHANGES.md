# Changes: Cybersecurity Log Analyzer (Phase 0 fixes)

**Goal:** make the project run from a fresh download, fix two security
issues, and add automated tests, **without changing your detection logic**.
Every rule, threshold and risk score works exactly as before.

---

## Summary

| # | Problem (before) | Fix (after) |
|---|---|---|
| 1 | Crashed on startup from any folder (`ModuleNotFoundError` / `FileNotFoundError`) | Proper `app/` package and absolute paths in `config.py` |
| 2 | **Stored XSS:** usernames from the log were inserted into the dashboard as raw HTML | `escapeHtml()` applied to every log value |
| 3 | CORS allowed every website (`*`) with credentials on | Only configured origins, no credentials, GET only |
| 4 | One malformed log line crashed the whole import | Bad lines are skipped with a warning |
| 5 | API returned errors (500) if started before ingesting a log | Table is created automatically; API returns empty results |
| 6 | Dashboard had to be opened as a local file | Served by the API at `/dashboard` |
| 7 | No dependency list | `requirements.txt` |
| 8 | No tests (`database_test.py` was a scratch script) | 33 pytest tests |
| 9 | Generated `security.db` could be committed by accident | `.gitignore` |

---

## 1. Project structure

**Before** (inside `cs-journey/Projects/cybersecurity_log_analyzer/`):

```text
main.py  log_event.py  database.py  log_analyzer.py  api.py
index.html  security.log  database_test.py  README.md
```

**After** (a standalone project, ready to be its own GitHub repo):

```text
app/
  __init__.py      NEW - makes app/ a Python package
  config.py        NEW - paths and settings in one place
  ingest.py        was main.py
  log_event.py     unchanged
  database.py      import fixed
  log_analyzer.py  timestamp format moved to config
  api.py           CORS, dashboard route, safe startup
static/index.html  was index.html (XSS fix + relative URLs)
data/security.log  was security.log (unchanged)
tests/             NEW - 33 tests
requirements.txt   NEW
.gitignore         NEW
CHANGES.md         NEW - this file
```

**Removed:** `database_test.py`. It was a manual experiment that wrote to
the real `security.db`, not a test. Its checks are now proper tests in
`tests/test_database.py`.

---

## 2. Why it crashed, and the fix

**Before:** files imported each other like this:

```python
from Projects.cybersecurity_log_analyzer.log_event import LogEvent
```

and opened files with relative names:

```python
with open("security.log", "r") as file:
db = DatabaseManager("security.db")
```

Those two things need **different** working folders:

- The import only works when you run from the `cs-journey` root.
- `"security.log"` only works when you run from the project folder.

So no single folder works for both. It probably ran for you because VS Code
was adding the repo root to the Python path.

**After:**

- Imports are short and package-based: `from app.log_event import LogEvent`.
- `app/config.py` builds every path from its own location:

```python
BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_PATH = Path(os.getenv("LOG_ANALYZER_DB", BASE_DIR / "security.db"))
DEFAULT_LOG_PATH = DATA_DIR / "security.log"
```

Now `python -m app.ingest` and `uvicorn app.api:app` work from the project
folder, and the test `test_main_runs_from_any_folder` proves the paths
don't depend on the current directory.

---

## 3. `main.py` → `app/ingest.py`

**Before:** all the code ran at the top level of the file, and every line
was split blindly:

```python
parts = line.strip().split("|")
event = LogEvent(parts[0], parts[1], parts[2], parts[3])
```

A line with fewer than 4 fields raised `IndexError`. A badly formatted
date was stored, then crashed the analyzer later inside `parse_timestamp`.

**After:**

- `parse_line(line)` returns `None` if the line doesn't have exactly 4
  non-empty fields, or if the timestamp isn't `YYYY-MM-DD HH:MM:SS`.
- `ingest_file(db, path)` skips bad lines, prints
  `Skipping malformed line 7: '...'`, and returns `(read, skipped)` counts.
- `main()` has command-line options (`--log`, `--db`), and the code only
  runs under `if __name__ == "__main__":`, so tests can import it safely.
- The printed report is identical to before, plus one summary line:
  `Read 11 events from ... (0 malformed lines skipped)`.

---

## 4. Security fix: stored XSS in the dashboard

**Before:** the dashboard built table rows like this:

```javascript
row.innerHTML = `<td>${event.username}</td>`;
```

Usernames come from login attempts, which **the attacker controls**. If an
attacker tried to log in with a username like:

```html
<img src=x onerror="...malicious JavaScript...">
```

the browser would run that JavaScript the moment an analyst opened the
dashboard. I tested this in a real browser: **the payload executed in the
original version.**

**After:** a helper escapes HTML special characters before insertion:

```javascript
function escapeHtml(value) {
    return String(value)
        .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;").replace(/'/g, "&#39;");
}
row.innerHTML = `<td>${escapeHtml(event.username)}</td>`;
```

It's applied to every value that comes from the API (IPs, usernames, event
types, timestamps, scores). With the same payload, the fixed version shows
it as plain text, and nothing executes.

**Interview angle:** "Log data is attacker-controlled input. I found that my
own dashboard was vulnerable to stored XSS through the username field and
fixed it by escaping output." That's a strong, true story.

---

## 5. Security fix: CORS

**Before:**

```python
allow_origins=["*"], allow_credentials=True, allow_methods=["*"]
```

`*` means any website on the internet may call the API from a visitor's
browser. Combining `*` with credentials is also invalid under the CORS
standard, and browsers refuse it.

**After:**

```python
allow_origins=config.ALLOWED_ORIGINS,   # http://127.0.0.1:8000, http://localhost:8000
allow_credentials=False,                # the API uses no cookies or logins
allow_methods=["GET"],                  # the API is read-only
```

You can change the allowed origins with the environment variable
`LOG_ANALYZER_ALLOWED_ORIGINS`, without editing code.

---

## 6. `api.py` other changes

| Before | After |
|---|---|
| `DatabaseManager("security.db")` repeated in 3 places | One `get_database()` helper using `config.DATABASE_PATH` |
| If no log had been ingested yet, endpoints failed with `no such table` | `get_database()` calls `create_table()` (safe to repeat), so endpoints return zeros/empty lists |
| Dashboard opened as a file, calling `http://127.0.0.1:8000/...` | New `GET /dashboard` route serves the page, and the page uses relative URLs (`/statistics`) |
| `FastAPI()` | `FastAPI(title="Cybersecurity Log Analyzer")`, which shows in `/docs` |

All endpoint responses (`/`, `/statistics`, `/suspicious-ips`, `/high-risk`,
`/events`) are **unchanged**.

---

## 7. Small changes in other files

- `database.py`: only the import line changed (plus one comment).
- `log_analyzer.py`: the timestamp format string moved to
  `config.TIMESTAMP_FORMAT`, so `ingest.py` and the analyzer always agree.
  All detection logic is untouched.
- `log_event.py` and `data/security.log`: unchanged.

---

## 8. Tests (new)

Run with `python -m pytest`.

| File | What it checks |
|---|---|
| `test_log_analyzer.py` (12 tests) | Failed-login counts, suspicious-IP threshold, brute force (fast vs slow failures, unsorted input), success after failures (including reset), unique usernames, risk score HIGH (10) and LOW (2), full report, empty log |
| `test_database.py` (7) | Round trip, duplicate events ignored, SQL suspicious-IP query, filters, **SQL-injection attempt returns nothing**, statistics, newest-first ordering |
| `test_ingest.py` (5) | Valid line parsing, 4 kinds of malformed line rejected, mixed file imports 2 and skips 1, sample log imports all 11, CLI works from an unrelated folder |
| `test_api.py` (9) | Every endpoint, dashboard served, works before ingest, CORS rejects unknown origins and allows configured ones |

**Verification status:** 24 tests were run and pass. The 9 API tests need
FastAPI and httpx, which I couldn't install in my workspace. Run
`pip install -r requirements.txt` and then `python -m pytest` to run all 33.
I checked the endpoint logic separately by calling each endpoint function
directly, and every response matched what the tests expect.

---

## Not changed yet (next phases)

These are deliberately left for you to build next, because you should be
able to explain them yourself in interviews:

- Performance: the analyzer still rescans all events for each IP (Phase 1).
- Real SSH `auth.log` parsing (Phase 1).
- The AI incident-report layer (Phase 2).
- Docker and GitHub Actions (Phase 3).
