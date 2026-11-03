students = {"Alice":85, "Bob":72, "Charlie": 91}

with open("students.txt", "w") as file:
    for student in students:
        file.write(f"{student},{students[student]}\n")

