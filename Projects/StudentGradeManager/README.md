# Student Management System

A command-line Python application for managing student records,
built to practise object-oriented programming.

## OOP Concepts Demonstrated

- Abstract classes (`Student` with abstract `course_info` and `student_type`)
- Inheritance (`ComputerScienceStudent`, `BusinessStudent`)
- Polymorphism (`display()`, `to_dict()` overridden per student type)
- Encapsulation (validated properties for name, mark and age)
- JSON persistence
- Error handling and input validation

## Features

- Add, find, remove and list students
- Update marks with validation (0-100, decimals allowed)
- Grades A-F and pass/fail status
- Find students by course
- Summary statistics by student type
- Save to and load from `students.json`

## Quick Start

```bash
python main.py
```

No external packages are needed to run the app. The data file is always
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
- Moved early file-handling practice scripts into `practice/`
- Added 17 pytest tests

## Project Structure

```text
main.py           Menu loop (program entry point)
menu.py           Menu display and validated input helpers
student.py        Student base class and the two student types
course.py         Course class
manager.py        StudentManager: storage, search, JSON save/load
test_students.py  pytest tests
students.json     Saved student data
practice/         Early file-handling practice scripts
```
