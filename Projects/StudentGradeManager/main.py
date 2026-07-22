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
    print()

choice = 0
students = {}

while choice != 5:
    display_menu()

    choice = int(input("Enter your choice: "))

    if choice == 1:
        name = input("Enter student name: ")
        
        if name in students:
            print("Student already exists!")
            print(f"Current mark: {students[name]}")
        
        else:
            mark = int(input("Enter mark: "))
            students[name] = mark
            print("Student added successfully!")

    elif choice == 2:
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

    elif choice == 3:
       
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

    elif choice == 4:
        total = 0
        
        for student in students:
            total += students[student]

        if students:
            avg = total / len(students)
            print(f"Average mark: {avg:.1f}")
        
        else:
            print("No students found")

    elif choice == 6:
        name = input("Enter student name: ")

        if name in students:
            print(f"Current mark: {students[name]}")
            new_mark = int(input("Enter new mark: "))

            students[name] = new_mark
        
            print("\nMark updated successfully!")        

        else:
            print("Student doesn't exist!")

    elif choice == 7:
        name = input("Enter student name: ")
        
        if name in students:
            students.pop(name)
            print(f"\nStudent {name} deleted successfully!")

        else:
            print("\nStudent not found")

    elif choice > 7 or choice < 1:
        print("Invalid choice! Please enter a number between 1 and 6")
print("Goodbye!")
    
