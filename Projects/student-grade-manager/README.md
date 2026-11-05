# Student Grade Manager

A command-line Python application for managing student records,
built to practise object-oriented programming.

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

No external packages are needed to run the app (SQLite is built into Python). The data file is always
read from and saved to the project folder, whichever folder you run it from.

## Running the Tests

```bash
pip install pytest
python -m pytest
```

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
test_students.py  pytest tests
students.db       Saved student data (created on first run)
```
