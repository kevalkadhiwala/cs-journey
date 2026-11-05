# ============================================================
# SYNTHETIC SEED DATA
# ============================================================
# Fills a database with made-up students and subject results, so the
# app can be demoed and tested without using anyone's real data.
# The same random_seed always gives the same students.

import random

from course import Course
from database import StudentDatabase
from student import BusinessStudent, ComputerScienceStudent

FIRST_NAMES = ["Aisha", "Liam", "Sofia", "Oisin", "Priya", "Jack", "Mei",
               "Conor", "Zara", "Daniel", "Niamh", "Arjun", "Emma", "Luca",
               "Chloe", "Sean", "Fatima", "Noah", "Grace", "Ravi"]
LAST_NAMES = ["Murphy", "Kelly", "Patel", "Byrne", "Chen", "Walsh", "Khan",
              "Ryan", "Silva", "Doyle", "Nowak", "O'Brien"]

TERMS = ["2025-S1", "2025-S2", "2026-S1"]

CS_COURSE = ("BSc Computer Science", "CS101")
CS_SUBJECTS = ["Programming", "Databases", "Networks", "Maths"]
CS_LANGUAGES = ["Python", "Java", "C++", "JavaScript"]

BUSINESS_COURSE = ("BSc Business", "BS200")
BUSINESS_SUBJECTS = ["Accounting", "Marketing", "Economics", "Maths"]
SPECIALISATIONS = ["Marketing", "Finance", "Management", "Analytics"]


def make_names(rng, count):
    # Every first/last pair once, shuffled, so names never repeat
    pairs = [f"{first} {last}" for first in FIRST_NAMES for last in LAST_NAMES]
    rng.shuffle(pairs)
    return pairs[:count]


def make_marks(rng, subjects):
    # Each student has an underlying ability, so their marks are
    # consistent across subjects instead of pure noise.
    ability = rng.gauss(60, 12)
    results = []

    for term in TERMS:
        for subject in subjects:
            mark = round(min(100, max(0, rng.gauss(ability, 8))))
            results.append((subject, term, mark))

    return results


def generate(count=30, random_seed=42):
    """Return (students, results) where results are (name, subject, term, mark)."""
    max_count = len(FIRST_NAMES) * len(LAST_NAMES)
    if not 1 <= count <= max_count:
        raise ValueError(f"count must be between 1 and {max_count}")

    rng = random.Random(random_seed)
    students = []
    results = []

    for name in make_names(rng, count):
        age = rng.randint(18, 24)

        if rng.random() < 0.5:
            subjects = CS_SUBJECTS
            course = Course(*CS_COURSE)
            make_student = lambda mark: ComputerScienceStudent(  # noqa: E731
                name, mark, age, rng.choice(CS_LANGUAGES), course)
        else:
            subjects = BUSINESS_SUBJECTS
            course = Course(*BUSINESS_COURSE)
            make_student = lambda mark: BusinessStudent(  # noqa: E731
                name, mark, age, rng.choice(SPECIALISATIONS), course)

        marks = make_marks(rng, subjects)

        # The overall mark is the average of the student's subject marks
        overall = round(sum(mark for _, _, mark in marks) / len(marks), 1)
        students.append(make_student(int(overall) if overall.is_integer() else overall))

        results.extend((name, subject, term, mark) for subject, term, mark in marks)

    return students, results


def seed_database(database_name, count=30, random_seed=42):
    database = StudentDatabase(database_name)

    if database.load_all():
        raise ValueError("database already has students; "
                         "use --db to seed a new file")

    students, results = generate(count, random_seed)

    database.save_all([student.to_dict() for student in students])
    for result in results:
        database.set_subject_mark(*result)

    return len(students), len(results)
