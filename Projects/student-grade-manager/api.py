# ============================================================
# REST API
# ============================================================
# Start with:   uvicorn api:app --reload
# Docs at:      http://127.0.0.1:8000/docs
#
# Read-only access to the same students.db the command line uses,
# plus the optional AI assistant at POST /ask.

import os
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

from assistant import StudentTools, ask
from database import StudentDatabase
from llm import LLMError, get_llm
from manager import StudentManager

PROJECT_DIR = Path(__file__).resolve().parent


def load_env_file(path=PROJECT_DIR / ".env"):
    # KEY=value lines; real environment variables win
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip("\"'"))


load_env_file()

app = FastAPI(title="Student Grade Manager")


def database_path():
    # Read on every request so tests can point it at a temporary file
    return Path(os.getenv("STUDENTS_DB", PROJECT_DIR / "students.db"))


def load_manager():
    manager = StudentManager()
    manager.load_from_database(database_path())
    return manager


def student_summary(student):
    # Names, courses and marks only: no ages leave the API
    return {
        "name": student.name,
        "student_type": student.student_type,
        "course_code": student.course.course_code,
        "mark": student.mark,
        "grade": student.get_grade(),
    }


@app.get("/")
def home():
    return {"message": "Student Grade Manager API is running!"}


@app.get("/students")
def list_students():
    students = load_manager().students
    return {"count": len(students),
            "students": [student_summary(s) for s in students]}


@app.get("/students/{name}")
def get_student(name: str):
    student = load_manager().find_student(name)

    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    return {**student_summary(student),
            "results": StudentDatabase(database_path()).get_subject_marks(name)}


@app.get("/subjects")
def list_subjects():
    return {"subjects": StudentDatabase(database_path()).list_subjects()}


def tidy_subject(subject):
    return " ".join(subject.split()).title()


TERM_QUERY = Query(default=None, pattern=r"^\d{4}-S[12]$",
                   description="e.g. 2026-S1; leave out for all terms")


@app.get("/subjects/{subject}/average")
def subject_average(subject: str, term: str | None = TERM_QUERY):
    subject = tidy_subject(subject)
    average, count = StudentDatabase(database_path()).subject_average(subject, term)

    if count == 0:
        raise HTTPException(status_code=404, detail=f"No results for {subject}")

    return {"subject": subject, "term": term, "average": average,
            "number_of_marks": count}


@app.get("/subjects/{subject}/below")
def students_below(subject: str, mark: float = Query(ge=0, le=100),
                   term: str | None = TERM_QUERY):
    subject = tidy_subject(subject)
    rows = StudentDatabase(database_path()).students_below(subject, mark, term)

    return {"subject": subject, "term": term, "below": mark, "count": len(rows),
            "students": rows}


class Question(BaseModel):
    question: str = Field(min_length=3, max_length=300)


@app.post("/ask")
def ask_question(body: Question):
    try:
        llm = get_llm()
    except LLMError as error:
        raise HTTPException(status_code=503, detail=f"AI settings problem: {error}")

    if llm is None:
        raise HTTPException(
            status_code=503,
            detail="The AI assistant is switched off (LLM_PROVIDER=off). "
                   "The /subjects endpoints give the same data without AI.")

    manager = load_manager()
    tools = StudentTools(StudentDatabase(database_path()),
                         {student.name for student in manager.students})

    return {"question": body.question, **ask(body.question, llm, tools)}
