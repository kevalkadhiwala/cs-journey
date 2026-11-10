class Course:

    def __init__(self, course_name, course_code):
        self.course_name = course_name
        self.course_code = course_code
        self.students = []

    def add_student(self, student):
        self.students.append(student)

    def display_students(self):
        if self.students:
            print("Enrolled students:")
            for student in self.students:
                print(student.name)
        else:
            print("No students Enrolled!")

    def remove_student(self, student):
        # No message here: StudentManager prints one, and printing in
        # both places showed "Student removed successfully!" twice
        if student in self.students:
            self.students.remove(student)

    def display(self):
        print(f"Course: {self.course_name}")
        print(f"Code: {self.course_code}")

