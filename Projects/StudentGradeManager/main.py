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
    print()

choice = 0
students = []

while choice != 5:
    display_menu()

    choice = int(input("Enter your choice: "))

    if choice == 1:
        name = input("Enter student name: ")
        students.append(name)
        print("Student added successfully!")

    elif choice == 2:
        if students:
            print("-" *5 + " Students " + "-" *5)
            print()
            
            i = 1
            for student in students:
                print(f"{i}. {student}")
                i += 1

            print("\n"+ "Total students:", len(students))
            print()
            print("-" * 20)
        else:
            print("No students found.")

    elif choice == 3:
       
        name = input("Enter student name: ")
        print()
        if name in students:
            print("Student found.")
        else:
            print("Student not found")

    elif choice == 4:
        print(f"You selected Calculate Average.")

    elif choice > 5 or choice < 1:
        print("Invalid choice! Please enter a number between 1 and 5")
print("Goodbye!")
    
