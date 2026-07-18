def display_menu():
    print("=" * 30)
    print("  Student Grade Manager")
    print("=" * 30)
    print("1. Add Student")
    print("2. View Students")
    print("3. Search Student")
    print("4. Calculate Average")
    print("5. Exit")

display_menu()

choice = input("Enter your choice: ")
print(f"You selected option {choice}")
