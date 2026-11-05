import argparse
import re

from course import Course
from database import StudentDatabase
from seed import seed_database
from student import BusinessStudent, ComputerScienceStudent

# ============================================================
# COMMAND-LINE INTERFACE
# ============================================================
# Lets the program be used without the menu, e.g.
#   python main.py list
#   python main.py add --type cs --name Aisha --mark 72 --age 20 ...
# Each command returns an exit code: 0 for success, 1 for an error.


def mark_type(value):
    # Same rules as the menu: a number from 0 to 100,
    # stored as an int when it is a whole number (70, not 70.0)
    try:
        mark = float(value)
    except ValueError:
        raise argparse.ArgumentTypeError("mark must be a number")

    if not 0 <= mark <= 100:
        raise argparse.ArgumentTypeError("mark must be between 0 and 100")

    return int(mark) if mark.is_integer() else mark


def term_type(value):
    # Terms look like 2026-S1 (year, then semester 1 or 2)
    value = value.strip().upper()

    if not re.fullmatch(r"\d{4}-S[12]", value):
        raise argparse.ArgumentTypeError("term must look like 2026-S1")

    return value


def subject_type(value):
    # "databases" and "Databases" are the same subject
    value = " ".join(value.split()).title()

    if not value:
        raise argparse.ArgumentTypeError("subject cannot be empty")

    return value


def build_parser():
    parser = argparse.ArgumentParser(
        description="Manage student records. Run with no command to open the menu."
    )
    parser.add_argument("--db", help="database file to use (default: students.db)")

    commands = parser.add_subparsers(dest="command", metavar="command")

    commands.add_parser("list", help="show every student")

    find = commands.add_parser("find", help="show one student")
    find.add_argument("name")

    add = commands.add_parser("add", help="add a student")
    add.add_argument("--type", required=True, choices=["cs", "business"])
    add.add_argument("--name", required=True)
    add.add_argument("--mark", required=True, type=mark_type)
    add.add_argument("--age", required=True, type=int)
    add.add_argument("--course-name", required=True)
    add.add_argument("--course-code", required=True)
    add.add_argument("--language", help="programming language (cs students)")
    add.add_argument("--specialisation", help="specialisation (business students)")

    remove = commands.add_parser("remove", help="remove a student")
    remove.add_argument("name")

    update = commands.add_parser("update-mark", help="change a student's mark")
    update.add_argument("name")
    update.add_argument("mark", type=mark_type)

    course = commands.add_parser("course", help="list students on a course")
    course.add_argument("course_code")

    commands.add_parser("summary", help="show student counts by type")

    result = commands.add_parser("add-result",
                                 help="record a mark for one subject and term")
    result.add_argument("name")
    result.add_argument("subject", type=subject_type)
    result.add_argument("term", type=term_type)
    result.add_argument("mark", type=mark_type)

    results = commands.add_parser("results", help="show a student's subject marks")
    results.add_argument("name")

    average = commands.add_parser("subject-average",
                                  help="class average for a subject")
    average.add_argument("subject", type=subject_type)
    average.add_argument("--term", type=term_type)

    below = commands.add_parser("below",
                                help="students under a mark in a subject")
    below.add_argument("subject", type=subject_type)
    below.add_argument("mark", type=mark_type)
    below.add_argument("--term", type=term_type)

    seed = commands.add_parser("seed",
                               help="fill a new database with made-up students")
    seed.add_argument("--count", type=int, default=30)
    seed.add_argument("--random-seed", type=int, default=42)

    return parser


def add_command(args, manager):
    if args.type == "cs" and not args.language:
        print("Error: --language is required for cs students.")
        return 1

    if args.type == "business" and not args.specialisation:
        print("Error: --specialisation is required for business students.")
        return 1

    if manager.find_student(args.name):
        print("Student already exists!")
        return 1

    course = Course(args.course_name, args.course_code)

    try:
        if args.type == "cs":
            student = ComputerScienceStudent(
                args.name, args.mark, args.age, args.language, course
            )
        else:
            student = BusinessStudent(
                args.name, args.mark, args.age, args.specialisation, course
            )
    except (ValueError, TypeError) as error:
        print(f"Error: {error}")
        return 1

    manager.add_student(student)
    return 0


def results_command(args, manager, database):
    if not manager.find_student(args.name):
        print("Student not found!")
        return 1

    marks = database.get_subject_marks(args.name)

    if not marks:
        print(f"No subject results for {args.name}.")
        return 0

    print(f"Results for {args.name}")
    current_term = None

    for row in marks:
        if row["term"] != current_term:
            current_term = row["term"]
            term_marks = [r["mark"] for r in marks if r["term"] == current_term]
            average = sum(term_marks) / len(term_marks)
            print()
            print(f"{current_term}  (average {average:.1f})")

        print(f"  {row['subject']:<15} {row['mark']}")

    return 0


def subject_command(args, database):
    # Handles both "subject-average" and "below"
    if args.subject not in database.list_subjects():
        print(f"No results for subject {args.subject}.")
        return 1

    where = f" in {args.term}" if args.term else ""

    if args.command == "subject-average":
        average, count = database.subject_average(args.subject, args.term)

        if count == 0:
            print(f"No {args.subject} results{where}.")
            return 1

        print(f"{args.subject} average{where}: {average} ({count} marks)")
        return 0

    rows = database.students_below(args.subject, args.mark, args.term)

    if not rows:
        print(f"Nobody is below {args.mark} in {args.subject}{where}.")
        return 0

    for row in rows:
        print(f"{row['student_name']:<20} {row['term']}  {row['mark']}")

    return 0


def run_command(args, manager, data_file):
    # Commands that change data save straight away,
    # because the program exits as soon as the command finishes.

    if args.command == "list":
        manager.display_students()

    elif args.command == "find":
        student = manager.find_student(args.name)

        if not student:
            print("Student not found!")
            return 1

        student.display()

    elif args.command == "add":
        result = add_command(args, manager)

        if result != 0:
            return result

        manager.save_to_database(data_file)

    elif args.command == "remove":
        student = manager.find_student(args.name)

        if not student:
            print("Student not found!")
            return 1

        manager.remove_student(student)
        manager.save_to_database(data_file)

    elif args.command == "update-mark":
        if not manager.find_student(args.name):
            print("Student not found!")
            return 1

        manager.update_mark(args.name, args.mark)
        manager.save_to_database(data_file)

    elif args.command == "course":
        students = manager.find_by_course(args.course_code)

        if not students:
            print("No students found for this course!")
            return 1

        for student in students:
            student.display()
            print()

    elif args.command == "summary":
        manager.display_summary()

    elif args.command == "add-result":
        if not manager.find_student(args.name):
            print("Student not found!")
            return 1

        StudentDatabase(data_file).set_subject_mark(
            args.name, args.subject, args.term, args.mark)
        print(f"Saved {args.subject} {args.term}: {args.mark}")

    elif args.command == "results":
        return results_command(args, manager, StudentDatabase(data_file))

    elif args.command in ("subject-average", "below"):
        return subject_command(args, StudentDatabase(data_file))

    elif args.command == "seed":
        try:
            students, results = seed_database(
                data_file, args.count, args.random_seed)
        except ValueError as error:
            print(f"Error: {error}")
            return 1

        print(f"Created {students} students with {results} subject results.")

    return 0
