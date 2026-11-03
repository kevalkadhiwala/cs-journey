def display_menu():
    print()
    print("1. Add student")
    print("2. View students")
    print("3. Find student")
    print("4. Remove student")
    print("5. Update mark")
    print("6. Find by course")
    print("7. Student summary")
    print("8. Save students")
    print("9. Exit")


# ------------------------------------------------------------
# Input helpers: keep asking until the user types something valid
# ------------------------------------------------------------

def get_menu_choice():
    while True:
        choice = input("Enter your choice (1-9): ").strip()

        if choice in {"1", "2", "3", "4", "5", "6", "7", "8", "9"}:
            return choice

        print("Invalid choice! Please enter a number from 1 to 9.")


def get_student_type():
    while True:
        print("1. Computer Science")
        print("2. Business")
        student_type = input("Enter student type (1-2): ").strip()

        if student_type in {"1", "2"}:
            return student_type

        print("Invalid student type! Please enter 1 or 2.")


def get_valid_mark():
    while True:
        try:
            mark = float(input("Enter mark (0-100): "))
        except ValueError:
            print("Mark must be a number.")
            continue

        if 0 <= mark <= 100:
            # Store whole numbers as int (70 rather than 70.0)
            return int(mark) if mark.is_integer() else mark

        print("Mark must be between 0 and 100.")


def get_valid_age():
    while True:
        try:
            age = int(input("Enter age: "))
        except ValueError:
            print("Age must be a whole number.")
            continue

        if age > 0:
            return age

        print("Age must be greater than 0.")
