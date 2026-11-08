# Runs the API and dashboard on port 8000.
#   docker build -t log-analyzer .
#   docker run -p 8000:8000 log-analyzer
FROM python:3.12-slim

WORKDIR /app

# Install packages first so Docker can reuse this layer when only code changes
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ app/
COPY data/ data/
COPY static/ static/

# Don't run as root. The database lives in its own folder so it can be
# kept on a volume: docker run -v log-data:/app/db ...
RUN useradd --create-home analyst && mkdir db && chown analyst db
USER analyst

ENV LOG_ANALYZER_DB=/app/db/security.db \
    PYTHONUNBUFFERED=1

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/')"

# Load the sample log (re-running is safe, duplicates are ignored), then serve
CMD ["sh", "-c", "python -m app.ingest && uvicorn app.api:app --host 0.0.0.0 --port 8000"]
