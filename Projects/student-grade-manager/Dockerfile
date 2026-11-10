# Runs the REST API on port 8000 with 30 made-up students.
#   docker build -t grade-manager .
#   docker run -p 8000:8000 grade-manager
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY *.py ./

RUN useradd --create-home teacher && mkdir data && chown teacher data
USER teacher

ENV STUDENTS_DB=/app/data/students.db \
    PYTHONUNBUFFERED=1

EXPOSE 8000

# Hosts like Render choose the port through $PORT; 8000 otherwise
HEALTHCHECK --interval=30s --timeout=5s \
    CMD python -c "import os, urllib.request as r; r.urlopen('http://127.0.0.1:' + os.getenv('PORT', '8000') + '/')"

# seed only fills an empty database, so a restart with a volume keeps
# existing data (it just prints an error and carries on)
CMD ["sh", "-c", "python main.py --db \"$STUDENTS_DB\" seed; uvicorn api:app --host 0.0.0.0 --port ${PORT:-8000}"]
