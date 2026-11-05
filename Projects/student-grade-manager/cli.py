import argparse

from course import Course
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

    return 0
