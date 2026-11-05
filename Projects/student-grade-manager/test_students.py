"""Run with:  python -m pytest"""
import pytest

from course import Course
from manager import StudentManager
from student import BusinessStudent, ComputerScienceStudent


def make_cs(name="Aisha", mark=72, age=20):
    return ComputerScienceStudent(name, mark, age, "Python", Course("BSc CS", "CS101"))


@pytest.mark.parametrize("mark, grade", [
    (100, "A"), (70, "A"), (69.5, "B"), (60, "B"), (59.9, "C"),
    (50, "C"), (40, "D"), (39.5, "F"), (0, "F"),
])
def test_grade_boundaries_including_decimals(mark, grade):
    assert make_cs(mark=mark).get_grade() == grade


@pytest.mark.parametrize("bad_mark, error", [
    (-1, ValueError), (101, ValueError), ("70", TypeError), (True, TypeError),
])
def test_invalid_marks_are_rejected(bad_mark, error):
    with pytest.raises(error):
        make_cs(mark=bad_mark)


def test_invalid_age_is_rejected():
    with pytest.raises(ValueError):
        make_cs(age=0)


def test_empty_name_is_rejected():
    with pytest.raises(ValueError):
        make_cs(name="   ")


def test_save_then_load_round_trip(tmp_path, capsys):
    data_file = tmp_path / "students.json"

    manager = StudentManager()
    manager.add_student(make_cs())
    manager.add_student(BusinessStudent("Tom", 55, 22, "Marketing",
                                        Course("Business", "BS200")))
    manager.save_students(data_file)

    reloaded = StudentManager()
    reloaded.load_students(data_file)

    assert reloaded.student_count() == 2
    assert reloaded.find_student("Aisha").programming_language == "Python"
    assert reloaded.find_student("Tom").specialisation == "Marketing"


def test_load_missing_file_starts_empty(tmp_path, capsys):
    manager = StudentManager()
    assert manager.load_students(tmp_path / "nope.json") == []
    assert "File does not exist!" in capsys.readouterr().out


# ------------------------------------------------------------
# SQLite storage
# ------------------------------------------------------------

def test_database_round_trip_keeps_both_student_types(tmp_path, capsys):
    db_file = tmp_path / "students.db"

    manager = StudentManager()
    manager.add_student(make_cs(mark=69.5))
    manager.add_student(BusinessStudent("Tom", 55, 22, "Marketing",
                                        Course("Business", "BS200")))
    manager.save_to_database(db_file)

    reloaded = StudentManager()
    reloaded.load_from_database(db_file)

    aisha = reloaded.find_student("Aisha")
    tom = reloaded.find_student("Tom")
    assert reloaded.student_count() == 2
    assert aisha.programming_language == "Python"
    assert aisha.mark == 69.5 and aisha.get_grade() == "B"
    assert tom.specialisation == "Marketing"
    assert tom.mark == 55 and isinstance(tom.mark, int)
    assert tom.course.course_code == "BS200"


def test_saving_again_replaces_old_rows(tmp_path, capsys):
    db_file = tmp_path / "students.db"

    manager = StudentManager()
    manager.add_student(make_cs())
    manager.save_to_database(db_file)

    manager.remove_student(manager.find_student("Aisha"))
    manager.add_student(make_cs(name="Ben"))
    manager.save_to_database(db_file)

    reloaded = StudentManager()
    reloaded.load_from_database(db_file)
    assert [s.name for s in reloaded.students] == ["Ben"]


def test_new_database_starts_empty(tmp_path):
    manager = StudentManager()
    assert manager.load_from_database(tmp_path / "new.db") == []


def test_json_data_can_be_moved_into_database(tmp_path, capsys):
    json_file = tmp_path / "students.json"
    db_file = tmp_path / "students.db"

    manager = StudentManager()
    manager.add_student(make_cs())
    manager.save_students(json_file)

    migrated = StudentManager()
    migrated.load_students(json_file)
    migrated.save_to_database(db_file)

    reloaded = StudentManager()
    reloaded.load_from_database(db_file)
    assert reloaded.find_student("Aisha").programming_language == "Python"


# ------------------------------------------------------------
# Command-line interface
# ------------------------------------------------------------

from main import main  # noqa: E402

ADD_AISHA = ["add", "--type", "cs", "--name", "Aisha", "--mark", "72",
             "--age", "20", "--course-name", "BSc CS", "--course-code", "CS101",
             "--language", "Python"]


def run(db_file, *args):
    return main(["--db", str(db_file), *args])


def test_cli_add_then_find(tmp_path, capsys):
    db_file = tmp_path / "cli.db"

    assert run(db_file, *ADD_AISHA) == 0
    assert run(db_file, "find", "Aisha") == 0

    output = capsys.readouterr().out
    assert "Name: Aisha" in output
    assert "Programming Language: Python" in output


def test_cli_add_requires_type_specific_field(tmp_path, capsys):
    db_file = tmp_path / "cli.db"
    without_language = ADD_AISHA[:-2]

    assert run(db_file, *without_language) == 1
    assert "--language is required" in capsys.readouterr().out


def test_cli_rejects_duplicate_student(tmp_path, capsys):
    db_file = tmp_path / "cli.db"
    run(db_file, *ADD_AISHA)

    assert run(db_file, *ADD_AISHA) == 1
    assert "already exists" in capsys.readouterr().out


def test_cli_update_mark_is_saved(tmp_path, capsys):
    db_file = tmp_path / "cli.db"
    run(db_file, *ADD_AISHA)

    assert run(db_file, "update-mark", "Aisha", "39.5") == 0

    manager = StudentManager()
    manager.load_from_database(db_file)
    assert manager.find_student("Aisha").get_grade() == "F"


def test_cli_remove_is_saved(tmp_path, capsys):
    db_file = tmp_path / "cli.db"
    run(db_file, *ADD_AISHA)

    assert run(db_file, "remove", "Aisha") == 0
    assert run(db_file, "find", "Aisha") == 1


def test_cli_course_and_summary(tmp_path, capsys):
    db_file = tmp_path / "cli.db"
    run(db_file, *ADD_AISHA)
    capsys.readouterr()

    assert run(db_file, "course", "CS101") == 0
    assert run(db_file, "course", "NOPE") == 1
    assert run(db_file, "summary") == 0
    assert "Computer Science: 1" in capsys.readouterr().out


@pytest.mark.parametrize("bad_mark", ["101", "-5", "abc"])
def test_cli_rejects_invalid_marks(tmp_path, bad_mark, capsys):
    # argparse prints the error and exits with code 2
    with pytest.raises(SystemExit) as error:
        run(tmp_path / "cli.db", "update-mark", "Aisha", bad_mark)
    assert error.value.code == 2


# ---------------- subject results and seed data ----------------

from database import StudentDatabase  # noqa: E402
from seed import generate  # noqa: E402


def run_cli(db_file, *args):
    return main(["--db", str(db_file), *args])


@pytest.fixture
def results_db(tmp_path, capsys):
    db_file = tmp_path / "results.db"
    run_cli(db_file, "add", "--type", "cs", "--name", "Aisha", "--mark", "72",
            "--age", "20", "--course-name", "BSc CS", "--course-code", "CS101",
            "--language", "Python")
    run_cli(db_file, "add", "--type", "cs", "--name", "Liam", "--mark", "48",
            "--age", "21", "--course-name", "BSc CS", "--course-code", "CS101",
            "--language", "Java")

    database = StudentDatabase(db_file)
    database.set_subject_mark("Aisha", "Databases", "2026-S1", 80)
    database.set_subject_mark("Liam", "Databases", "2026-S1", 35)
    database.set_subject_mark("Liam", "Databases", "2025-S2", 50)
    capsys.readouterr()
    return db_file


def test_same_subject_and_term_replaces_the_mark(results_db):
    database = StudentDatabase(results_db)
    database.set_subject_mark("Aisha", "Databases", "2026-S1", 64)

    assert database.get_subject_marks("Aisha") == [
        {"subject": "Databases", "term": "2026-S1", "mark": 64}
    ]


def test_subject_average_overall_and_by_term(results_db):
    database = StudentDatabase(results_db)

    assert database.subject_average("Databases") == (55.0, 3)
    assert database.subject_average("Databases", "2026-S1") == (57.5, 2)
    assert database.subject_average("Networks") == (None, 0)


def test_students_below_a_mark(results_db):
    rows = StudentDatabase(results_db).students_below("Databases", 60)

    assert [(r["student_name"], r["term"]) for r in rows] == [
        ("Liam", "2026-S1"), ("Liam", "2025-S2")
    ]


def test_removing_a_student_removes_their_results(results_db, capsys):
    run_cli(results_db, "remove", "Liam")

    database = StudentDatabase(results_db)
    assert database.get_subject_marks("Liam") == []
    assert database.subject_average("Databases") == (80.0, 1)


def test_cli_add_result_normalises_subject_and_term(results_db, capsys):
    assert run_cli(results_db, "add-result", "Aisha", "networks", "2026-s1", "66") == 0

    marks = StudentDatabase(results_db).get_subject_marks("Aisha")
    assert {"subject": "Networks", "term": "2026-S1", "mark": 66} in marks


def test_cli_add_result_needs_a_known_student(results_db, capsys):
    assert run_cli(results_db, "add-result", "Nobody", "Maths", "2026-S1", "50") == 1
    assert "Student not found!" in capsys.readouterr().out


@pytest.mark.parametrize("bad_term", ["2026", "2026-S3", "S1-2026"])
def test_cli_rejects_bad_terms(results_db, bad_term, capsys):
    with pytest.raises(SystemExit) as error:
        run_cli(results_db, "add-result", "Aisha", "Maths", bad_term, "50")
    assert error.value.code == 2


def test_cli_results_and_queries(results_db, capsys):
    run_cli(results_db, "results", "Liam")
    out = capsys.readouterr().out
    assert "2025-S2  (average 50.0)" in out
    assert "2026-S1  (average 35.0)" in out

    run_cli(results_db, "subject-average", "databases", "--term", "2026-S1")
    assert "Databases average in 2026-S1: 57.5 (2 marks)" in capsys.readouterr().out

    run_cli(results_db, "below", "Databases", "40")
    assert "Liam" in capsys.readouterr().out

    assert run_cli(results_db, "subject-average", "Art") == 1


def test_seed_data_is_repeatable_and_valid():
    students, results = generate(count=10, random_seed=7)
    again, _ = generate(count=10, random_seed=7)

    assert [s.name for s in students] == [s.name for s in again]
    assert len({s.name for s in students}) == 10
    # 4 subjects x 3 terms for every student
    assert len(results) == 120
    assert all(0 <= mark <= 100 for *_, mark in results)


def test_cli_seed_fills_only_an_empty_database(tmp_path, capsys):
    db_file = tmp_path / "seed.db"

    assert run_cli(db_file, "seed", "--count", "5") == 0
    assert "Created 5 students with 60 subject results." in capsys.readouterr().out

    assert run_cli(db_file, "seed") == 1
    assert "already has students" in capsys.readouterr().out
