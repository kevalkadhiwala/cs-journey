# Changes: Student Management System

**Goal:** make the program actually run, fix the save/load bug and the
grade bug, and add tests, keeping your OOP design the same.

---

## Summary

| # | Problem (before) | Fix (after) |
|---|---|---|
| 1 | `main.py` crashed immediately: `NameError: name 'StudentManager' is not defined` | Every file imports what it uses |
| 2 | Four input functions used by `main.py` didn't exist anywhere | Written in `menu.py` |
| 3 | **Save/load bug:** loaded `student.json` but saved `students.json`, so saved data never reloaded | One `DATA_FILE` constant used for both |
| 4 | Decimal marks like 69.5 got the grade `"Invalid marks!"` | Grade checks rewritten top-down |
| 5 | `True`/`False` were accepted as a mark or age | Rejected with `TypeError` |
| 6 | Student classes lived outside the project folder (`Projects/students.py`) | Moved into the project as `student.py` |
| 7 | No tests | 17 pytest tests |

---

## 1. The crash on startup

**Before:** the code was split across files, but the files never imported
each other. `main.py` used `StudentManager`, `Course`, `display_menu` and
others with no imports. `manager.py` used `json`, `Course`,
`ComputerScienceStudent` and `BusinessStudent` with no imports. The program
stopped on its first line of real code.

**After:**

`manager.py` now starts with:

```python
import json

from course import Course
from student import BusinessStudent, ComputerScienceStudent
```

`main.py` now starts with:

```python
from pathlib import Path

from course import Course
from manager import StudentManager
from menu import (display_menu, get_menu_choice, get_student_type,
                  get_valid_age, get_valid_mark)
from student import BusinessStudent, ComputerScienceStudent
```

---

## 2. Missing input functions

**Before:** `main.py` called `get_menu_choice()`, `get_student_type()`,
`get_valid_mark()` and `get_valid_age()`, but these functions weren't
defined in any file in the repo.

**After:** all four are in `menu.py`. Each one keeps asking until the
input is valid:

- `get_menu_choice()` accepts only 1-9.
- `get_student_type()` accepts only 1 (Computer Science) or 2 (Business).
- `get_valid_mark()` accepts a number from 0 to 100, decimals allowed.
  Whole numbers are stored as `int` (`70`, not `70.0`).
- `get_valid_age()` accepts a whole number greater than 0.

---

## 3. Save/load bug

**Before:**

```python
manager.load_students("student.json")    # at startup
manager.save_students("students.json")   # option 8 and on exit
```

The filenames differ by one letter, so the program saved to one file and
loaded from another. Every restart began with no students. Both names
were also relative, so the file location depended on which folder you ran
the program from.

**After:**

```python
DATA_FILE = Path(__file__).resolve().parent / "students.json"
manager.load_students(DATA_FILE)
manager.save_students(DATA_FILE)   # both save points
```

Tested: I added two students, saved, exited, then ran the program again
**from a different folder**, and both students loaded correctly.

---

## 4. Grade bug (`student.py`, `get_grade`)

**Before:**

```python
if 70 <= self._mark <= 100:  return "A"
elif 60 <= self._mark <= 69: return "B"
...
else: return "Invalid marks!"
```

Marks are allowed to be decimals, so a mark of **69.5** is neither
`<= 69` nor `>= 70`, and it returned `"Invalid marks!"`. The same gap
existed between every pair of grades (59.5, 49.5, 39.5).

**After:**

```python
if self._mark >= 70:   return "A"
elif self._mark >= 60: return "B"
elif self._mark >= 50: return "C"
elif self._mark >= 40: return "D"
return "F"
```

Checking from the top down leaves no gaps. The "invalid" branch isn't
needed, because the `mark` setter already guarantees 0-100.

---

## 5. Smaller fixes in `student.py`

- **Booleans rejected.** In Python, `True` is a subclass of `int`, so
  `mark = True` used to be stored as 1. Mark and age now reject booleans
  explicitly.
- **Clearer error message.** "Mark must be btw 0 and 100" became
  "Mark must be between 0 and 100."
- **Removed dead code.** `Student.save_students()` was an empty method
  (`pass`). Saving is the manager's job, so it was removed.
- **Removed an unused import.** `import json` wasn't used in this file.

All the OOP structure is unchanged: the abstract base class, both
subclasses, properties, `__eq__`, `to_dict()` and `display()`.

---

## 6. Files

| File | Status |
|---|---|
| `main.py` | Imports added, `DATA_FILE` constant, filenames fixed |
| `manager.py` | Imports added (logic unchanged) |
| `menu.py` | Four input helper functions added |
| `student.py` | Moved from `Projects/students.py` into this folder, fixes above |
| `course.py` | Unchanged |
| `test_students.py` | **New**, 17 tests |
| `students.json` | Empty starter file (`[]`) |
| `README.md` | Rewritten with quick start, tests and structure |

**Not carried over:** `try_practice.py`, `file_practice.py`,
`read_practice.py` and `students.txt` (practice files from the earlier
version). They're still in your original repo. I'd move them into a
`practice/` folder or remove them from the showcase repo.

---

## 7. Tests (new)

Run with `pip install pytest`, then `python -m pytest`. All 17 pass.

- Grade boundaries, including decimals (69.5 → B, 39.5 → F)
- Invalid marks rejected (-1, 101, "70", True)
- Invalid age and empty name rejected
- Save → load round trip keeps both student types and their extra fields
- Loading a missing file starts empty instead of crashing

---

## Known limitation (for the AI rewrite)

Each student gets its own `Course` object, even when two students share a
course code, so `course.students` only ever holds one student. "Find by
course" still works, because it searches by course code. This will go away
when the data moves to SQLite in the AI version.
