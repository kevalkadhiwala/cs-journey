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
