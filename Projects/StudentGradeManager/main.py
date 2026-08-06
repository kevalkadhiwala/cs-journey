def display_menu():
    print()
    print("=" * 30)
    print("  Student Grade Manager")
    print("=" * 30)
    print("1. Add Student")
    print("2. View Students")
    print("3. Search Student")
    print("4. Calculate Average")
    print("5. Exit")
    print("6. Update Student")
    print("7. Delete Student")
    print("8. Highest Mark")
    print("9. Lowest Mark")
    print()

def add_student(students):
    name = input("Enter student name: ")
        
    if name in students:
        print("Student already exists!")
        print(f"Current mark: {students[name]}")
        
    else:
        mark = -1
        while mark > 100 or mark < 0:
            try:
                mark = int(input("Enter mark: "))
                
            except ValueError:
                print("Please enter a valid number.")
                continue

            if 0 <= mark <= 100:
                students[name] = mark
                print("Student added successfully!")
                break
            else:
                print("Invalid mark! Please enter a mark between 0 and 100.")

def view_students(students):
    if students:
        print("-" *5 + " Students " + "-" *5)
        print()
            
        i = 1
        for student in students:
            print(f"{i}. {student} : {students[student]}")
            i += 1

        print("\n"+ "Total students:", len(students))
        print()
        print("-" * 20)
        
    else:
        print("No students found.")    

def search_student(students):
    name = input("Enter student name: ")
    print()
    found = False
        
    for student in students:
        
        if name in student:
            print("Student found!")
            print()
            print(f"Name : {student}")
            print(f"Mark : {students[student]}")
            found = True
            break

    if not found:    
        print("Student not found")

def calculate_average(students):
    total = 0
        
    for student in students:
        total += students[student]

    if students:
        avg = total / len(students)
        print(f"Average mark: {avg:.1f}")
        
    else:
        print("No students found")

def update_student(students):
    name = input("Enter student name: ")

    if name in students:
        print(f"Current mark: {students[name]}")
        new_mark = -1
        while new_mark < 0 or new_mark > 100:
            try:
                new_mark = int(input("Enter new mark: "))
            except ValueError:
                print("Please enter a valid number.")
                continue

            if 0 <= new_mark <= 100:
                students[name] = new_mark
                print("\nMark updated successfully!")
                break
            else:
                print("Invalid mark! Please enter a mark between 0 and 100.") 

    else:
        print("Student doesn't exist!")

def delete_student(students):
    name = input("Enter student name: ")
        
    if name in students:
        students.pop(name)
        print(f"\nStudent {name} deleted successfully!")

    else:
        print("\nStudent not found")

def highest_mark(students):
    if students:
        highest_name = ""
        highest_mark = -1
        for student in students:
            if students[student] > highest_mark:
                highest_mark = students[student]
                highest_name = student 
        print(f"{highest_name}: {highest_mark}")

    else:
        print("No students found!")

def lowest_mark(students):    
    if students:
        lowest_name = ""
        lowest_mark = 101
        for student in students:
            if students[student] < lowest_mark:
                lowest_mark = students[student]
                lowest_name = student 
        print(f"{lowest_name}: {lowest_mark}")

    else:
        print("No students found!")


choice = 0
students = {}

with open("students.txt", "r") as file:
    students = {}
    for line in file:
        line = line.strip()
        name, mark = line.split(",")
        students[name] = int(mark)

while choice != 5:
    display_menu()

    try:
        choice = int(input("Enter your choice: "))

    except ValueError:
        print("Invalid input! Please enter a number btw 1 and 9.")
        continue

    if choice == 1:
        add_student(students)

    elif choice == 2:
        view_students(students)

    elif choice == 3:
       search_student(students)

    elif choice == 4:
        calculate_average(students)

    elif choice == 6:
        update_student(students)

    elif choice == 7:
        delete_student(students)

    elif choice == 8:
        highest_mark(students)

    elif choice == 9:
        lowest_mark(students)

    elif choice > 9 or choice < 1:
        print("Invalid choice! Please enter a number between 1 and 6")

with open("students.txt", "w") as file:
    for name,mark in students.items():
        file.write(f"{name},{mark}\n")
print("Goodbye!")
    
