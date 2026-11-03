with open("students.txt", "r") as file:
    students = {}
    for line in file:
        line = line.strip()
        name, mark = line.split(",")
        students[name] = int(mark)
    print(students)