"""Tests for the REST API and the AI assistant. No real model is used:
FakeLLM plays the model with prepared replies."""
import json

import pytest

pytest.importorskip("fastapi")
pytest.importorskip("httpx")

from fastapi.testclient import TestClient  # noqa: E402

import api  # noqa: E402
from assistant import StudentTools, ask  # noqa: E402
from database import StudentDatabase  # noqa: E402
from llm import LLMError  # noqa: E402
from seed import seed_database  # noqa: E402


class FakeLLM:
    def __init__(self, *replies):
        self.replies = list(replies)
        self.prompts = []

    def complete(self, system, user):
        self.prompts.append(user)
        reply = self.replies.pop(0)
        if isinstance(reply, Exception):
            raise reply
        return reply if isinstance(reply, str) else json.dumps(reply)


@pytest.fixture
def db_file(tmp_path):
    path = tmp_path / "api.db"
    seed_database(path, count=12, random_seed=3)
    return path


@pytest.fixture
def client(db_file, monkeypatch):
    monkeypatch.setenv("STUDENTS_DB", str(db_file))
    monkeypatch.setenv("LLM_PROVIDER", "off")
    return TestClient(api.app)


@pytest.fixture
def tools(db_file):
    names = {row["name"] for row in StudentDatabase(db_file).load_all()}
    return StudentTools(StudentDatabase(db_file), names)


# ---------------- plain endpoints ----------------

def test_list_students_hides_ages(client):
    data = client.get("/students").json()

    assert data["count"] == 12
    assert "age" not in data["students"][0]
    assert {"name", "mark", "grade"} <= set(data["students"][0])


def test_one_student_with_results(client):
    name = client.get("/students").json()["students"][0]["name"]
    data = client.get(f"/students/{name}").json()

    assert len(data["results"]) == 12   # 4 subjects x 3 terms
    assert client.get("/students/Nobody").status_code == 404


def test_subject_average_and_below(client, db_file):
    expected, count = StudentDatabase(db_file).subject_average("Maths", "2026-S1")

    data = client.get("/subjects/maths/average", params={"term": "2026-S1"}).json()
    assert data == {"subject": "Maths", "term": "2026-S1",
                    "average": expected, "number_of_marks": count}

    below = client.get("/subjects/Maths/below", params={"mark": 100}).json()
    assert below["count"] == 36          # every Maths mark is below 100


@pytest.mark.parametrize("url", [
    "/subjects/Maths/average?term=2026-S3",
    "/subjects/Maths/below?mark=150",
    "/subjects/Maths/below",
])
def test_bad_query_values_are_rejected(client, url):
    assert client.get(url).status_code == 422


def test_ask_needs_ai_switched_on(client):
    response = client.post("/ask", json={"question": "Who is failing Maths?"})

    assert response.status_code == 503
    assert "switched off" in response.json()["detail"]


# ---------------- the assistant ----------------

def test_tool_call_then_grounded_answer(tools, db_file):
    average, _ = StudentDatabase(db_file).subject_average("Maths")
    fake = FakeLLM(
        {"tool": "class_average", "arguments": {"subject": "maths"}},
        {"answer": f"The Maths average is {average}."},
    )

    result = ask("What is the Maths average?", fake, tools)

    assert result["error"] is None
    assert result["answer"] == f"The Maths average is {average}."
    assert result["steps"][0]["result"]["subject"] == "Maths"
    # The tool result was shown to the model before it answered
    assert str(average) in fake.prompts[1]


def test_invented_numbers_are_rejected(tools):
    fake = FakeLLM(
        {"tool": "class_average", "arguments": {"subject": "Maths"}},
        {"answer": "The Maths average is 99.9."},
        {"answer": "The Maths average is 12.3."},
    )

    result = ask("What is the Maths average?", fake, tools)

    assert result["answer"] is None
    assert "checked answer" in result["error"]
    assert "99.9" in fake.prompts[2]     # the model was told what was wrong


def test_unknown_tools_and_bad_arguments_are_refused(tools):
    fake = FakeLLM(
        {"tool": "run_sql", "arguments": {"query": "DROP TABLE students"}},
        {"tool": "students_below", "arguments": {"subject": "Maths", "mark": 500}},
        {"answer": "I could not run that."},
    )

    result = ask("Delete everything", fake, tools)

    assert result["steps"] == []          # nothing was ever run
    assert result["answer"] == "I could not run that."
    assert "Input should be" in fake.prompts[1]


def test_unknown_student_gets_an_error_not_data(tools):
    fake = FakeLLM(
        {"tool": "student_results", "arguments": {"name": "Not A Student"}},
        {"answer": "There is no student with that name."},
    )

    result = ask("How is Not A Student doing?", fake, tools)
    assert "error" in result["steps"][0]["result"]


def test_tool_calls_are_limited(tools):
    calls = [{"tool": "class_average", "arguments": {"subject": subject}}
             for subject in ["Maths", "Databases", "Networks", "Programming",
                             "Accounting"]]
    fake = FakeLLM(*calls, "not json either")

    result = ask("Loop forever", fake, tools)

    assert len(result["steps"]) == 4
    assert result["answer"] is None


def test_term_the_question_never_mentioned_is_dropped(tools, db_file):
    overall, _ = StudentDatabase(db_file).subject_average("Maths")
    fake = FakeLLM(
        {"tool": "class_average", "arguments": {"subject": "Maths", "term": "2026-S1"}},
        {"answer": f"The Maths average is {overall}."},
    )

    result = ask("What is the Maths average?", fake, tools)

    assert result["steps"][0]["result"]["term"] is None
    assert result["answer"] == f"The Maths average is {overall}."


def test_term_in_the_question_is_kept(tools):
    fake = FakeLLM(
        {"tool": "class_average", "arguments": {"subject": "Maths", "term": "2026-S1"}},
        {"answer": "Done."},
    )

    result = ask("What is the Maths average in 2026-s1?", fake, tools)

    assert result["steps"][0]["result"]["term"] == "2026-S1"


def test_answer_naming_only_some_students_is_rejected(tools, db_file):
    rows = StudentDatabase(db_file).students_below("Maths", 100)
    names = [row["student_name"] for row in rows]
    assert len(names) >= 2

    fake = FakeLLM(
        {"tool": "students_below", "arguments": {"subject": "Maths", "mark": 100}},
        {"answer": f"Only {names[0]}."},
        {"answer": "Below 100: " + ", ".join(names) + "."},
    )

    result = ask("Who is below 100 in Maths?", fake, tools)

    assert "leaves out students" in fake.prompts[2]
    assert all(name in result["answer"] for name in names)


def test_repeated_tool_call_is_not_run_twice(tools):
    # What llama3.2 actually did: asked for the same data over and over
    call = {"tool": "list_subjects", "arguments": {}}
    fake = FakeLLM(call, call, {"answer": "Maths and Databases have results."})

    result = ask("Which subjects have results?", fake, tools)

    assert len(result["steps"]) == 1
    assert "already called list_subjects" in fake.prompts[2]
    assert result["answer"] == "Maths and Databases have results."


def test_model_outage_is_reported(tools):
    result = ask("Anything", FakeLLM(LLMError("could not reach the model")), tools)
    assert result == {"answer": None, "steps": [], "error": "could not reach the model"}


def test_ask_endpoint_uses_the_configured_model(client, monkeypatch):
    fake = FakeLLM({"tool": "list_subjects", "arguments": {}},
                   {"answer": "Subjects include Maths and Databases."})
    monkeypatch.setattr(api, "get_llm", lambda: fake)

    data = client.post("/ask", json={"question": "Which subjects are there?"}).json()

    assert data["answer"] == "Subjects include Maths and Databases."
    assert data["steps"][0]["tool"] == "list_subjects"
    assert "Maths" in data["steps"][0]["result"]["subjects"]
