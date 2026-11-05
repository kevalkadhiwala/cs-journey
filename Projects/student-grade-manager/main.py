# ============================================================
# MAIN PROGRAM
# ============================================================

import sys
from pathlib import Path

from cli import build_parser, run_command
from course import Course
from manager import StudentManager
from menu import (display_menu, get_menu_choice, get_student_type,
                  get_valid_age, get_valid_mark)
from student import BusinessStudent, ComputerScienceStudent

# Data lives next to this file, so the program finds it
# whichever folder you run it from.
PROJECT_DIR = Path(__file__).resolve().parent
DATA_FILE = PROJECT_DIR / "students.db"
OLD_JSON_FILE = PROJECT_DIR / "students.json"


def load_manager(data_file):
    manager = StudentManager()

    # One-time move from the old JSON file to the default database
    # (a custom --db file starts fresh instead)
    if data_file == DATA_FILE and not data_file.exists() and OLD_JSON_FILE.exists():
        manager.load_students(OLD_JSON_FILE)
        manager.save_to_database(data_file)
        print(f"Imported {manager.student_count()} students from students.json")

    manager.load_from_database(data_file)

    return manager


def run_menu(manager, data_file):
    while True:
        display_menu()

        choice = get_menu_choice()

        if choice == "9":
            save_choice = input(
                "Save changes before exiting? (y/n): "
            ).lower()

            if save_choice == "y":

                manager.save_to_database(data_file)

            print("Goodbye!")

            break

        elif choice == "1":

            student_type = get_student_type()

            name = input("Enter student name: ")

            mark = get_valid_mark()

            age = get_valid_age()
 
            course_name = input("Enter course name: ")
            course_code = input("Enter course code: ")

            course = Course(course_name, course_code)

            if student_type == "1":
                programming_language = input("Enter your programming language: ")
                student = ComputerScienceStudent(
                    name, mark, age,
                    programming_language, course
                )
                manager.add_student(student)

            elif student_type == "2":
                specialisation = input("Enter your specialisation: ")
                student = BusinessStudent(
                    name, mark, age,
                    specialisation, course
                )
                manager.add_student(student)

            else:
                print("Invalid student type!")

        elif choice == "2":
            manager.display_students()

        elif choice == "3":

            name = input("Enter student name: ")
            student = manager.find_student(name)

            if student:
                student.display()
            else:
                print("Student not found!")

        elif choice == "4":
            name = input("Enter student name: ")
            student = manager.find_student(name)

            if student:
                manager.remove_student(student)
            else:
                print("Student not found!")

        elif choice == "5":
            name = input("Enter student name: ")
            new_mark = get_valid_mark()

            manager.update_mark(name, new_mark)

        elif choice == "6":
            course_code = input("Enter your course code: ")
            students = manager.find_by_course(course_code)

            if students:
                for student in students:
                    student.display()
                    print()
            else:
                print("No students found for this course!")

        elif choice == "7":
            manager.display_summary()

        elif choice == "8":
            manager.save_to_database(data_file)


def main(argv=None):
    args = build_parser().parse_args(argv)

    data_file = Path(args.db) if args.db else DATA_FILE
    manager = load_manager(data_file)

    # No command given: open the interactive menu as before
    if args.command is None:
        run_menu(manager, data_file)
        return 0

    return run_command(args, manager, data_file)


if __name__ == "__main__":
    sys.exit(main())
