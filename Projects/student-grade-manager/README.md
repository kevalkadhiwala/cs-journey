# Student Grade Manager

A Python application for managing student records and subject results,
with a command line, a REST API and an optional AI assistant.
Started as an object-oriented programming exercise.

## OOP Concepts Demonstrated

- Abstract classes (`Student` with abstract `course_info` and `student_type`)
- Inheritance (`ComputerScienceStudent`, `BusinessStudent`)
- Polymorphism (`display()`, `to_dict()` overridden per student type)
- Encapsulation (validated properties for name, mark and age)
- SQLite persistence (JSON still supported for import)
- Error handling and input validation

## Features

- Add, find, remove and list students
- Update marks with validation (0-100, decimals allowed)
- Grades A-F and pass/fail status
- Find students by course
- Summary statistics by student type
- Save to and load from a SQLite database (`students.db`)
- Existing `students.json` data is imported automatically on first run
- Command-line commands (`list`, `add`, `find`, ...) as well as the interactive menu
- Marks per subject and per term (e.g. Databases, 2026-S1), with term averages
- Class averages per subject and a list of students below a mark
- Synthetic seed data, so the app can be demoed without real student data
- REST API (FastAPI) with validated query parameters
- Optional AI assistant: plain-English questions answered through safe tool calls

## Quick Start

```bash
python main.py
```

This opens the interactive menu. Every action is also available as a
command, which is handy for scripting:

```bash
python main.py list
python main.py find Aisha
python main.py add --type cs --name Aisha --mark 72 --age 20     --course-name "BSc CS" --course-code CS101 --language Python
python main.py add --type business --name Tom --mark 55 --age 22     --course-name Business --course-code BS200 --specialisation Marketing
python main.py update-mark Aisha 68.5
python main.py remove Tom
python main.py course CS101
python main.py summary
python main.py --help
```

### Subject results

Each student can have one mark per subject per term. Terms look like
`2026-S1` (year and semester); subject names are tidied, so
`databases` and `Databases` are the same subject.

```bash
python main.py --db demo.db seed            # 30 made-up students, 360 results
python main.py --db demo.db results "Aisha Doyle"
python main.py --db demo.db add-result "Aisha Doyle" Databases 2026-S1 74
python main.py --db demo.db subject-average Maths --term 2026-S1
python main.py --db demo.db below Databases 40
```

`seed` only fills an empty database, so it can never overwrite real
records. The data is random but repeatable (`--random-seed`), and each
student has a consistent "ability", so their marks look realistic.

Commands that change data save immediately. Use `--db path/to/file.db`
to work with a different database file.

The command line needs no external packages (SQLite is built into Python). The data file is always
read from and saved to the project folder, whichever folder you run it from.

## REST API

```bash
pip install -r requirements.txt
uvicorn api:app --reload        # then open http://127.0.0.1:8000/docs
```

| Endpoint | Description |
|---|---|
| `GET /students` | All students: name, type, course, mark, grade (no ages) |
| `GET /students/{name}` | One student with their subject results |
| `GET /subjects` | Subjects that have results |
| `GET /subjects/{subject}/average?term=` | Class average, optionally for one term |
| `GET /subjects/{subject}/below?mark=&term=` | Students under a mark |
| `POST /ask` | Optional AI assistant (see below) |

Bad values (a term like `2026-S3`, a mark of 150) are rejected with 422.

## AI Assistant (optional)

`POST /ask` with `{"question": "Who is below 40 in Databases in 2026-S1?"}`.

The model never touches the database or writes SQL. It works through
**tool calling**: it may only ask for one of four read-only functions,
and this code runs them:

| Tool | What it returns |
|---|---|
| `list_subjects` | Subject names |
| `class_average(subject, term?)` | Average and number of marks |
| `students_below(subject, mark, term?)` | Names and marks under a threshold |
| `student_results(name)` | One student's subject marks |

```text
question -> model asks for a tool -> arguments validated (Pydantic)
         -> tool runs on SQLite -> result back to the model
         -> model answers -> every number checked against tool results
```

Safeguards:

- **Allow-list of tools.** Unknown tools (`run_sql`) and bad arguments
  (a mark of 500) are refused and the model is told why. Nothing runs.
- **Grounded numbers.** Every number in the answer must appear in a tool
  result or the question, so the model cannot invent a mark or average.
  An answer that fails is retried once, then refused, and the raw tool
  results are returned instead.
- **Limits.** At most 4 tool calls per question.
- **Privacy.** Tools return names and marks only, and the demo data is
  synthetic.
- **Off by default.** With `LLM_PROVIDER=off`, `/ask` returns 503 and
  every other endpoint works as normal. Copy `.env.example` to `.env`
  to choose Ollama or an OpenAI-compatible API.
- **Tested without a network** using a fake model.

## Running the Tests

```bash
pip install -r requirements.txt
python -m pytest
```

56 tests cover the student classes, the database, the command line,
the REST API and the AI assistant's safeguards.

## Improvements

- Fixed missing imports that stopped `main.py` from starting
- Fixed a save/load mismatch so saved students now reload correctly
- Decimal marks (e.g. 69.5) now receive the correct grade
- `True`/`False` are rejected as marks or ages
- Moved the student classes into the project as `student.py`
- Added 17 pytest tests

## Project Structure

```text
main.py           Program entry point: menu or command
cli.py            Command-line arguments (argparse)
menu.py           Menu display and validated input helpers
student.py        Student base class and the two student types
course.py         Course class
manager.py        StudentManager: storage, search, save/load
database.py       SQLite storage: students and subject results
seed.py           Synthetic (made-up) demo data
api.py            FastAPI REST API
assistant.py      AI assistant: safe tools, validation, number checks
llm.py            Swappable LLM providers (off / Ollama / OpenAI-compatible)
test_api.py       API and assistant tests (fake model, no network)
test_students.py  pytest tests
students.db       Saved student data (created on first run)
```
