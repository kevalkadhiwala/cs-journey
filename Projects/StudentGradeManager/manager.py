class StudentManager:

    def __init__(self):
        self.students = []

    def add_student(self, student):
        if student in self.students:
            print("Student already exists!")

        else:
            self.students.append(student)
            student.course.add_student(student)

            print("Student added successfully!")

    def remove_student(self, student):
        if student in self.students:
            self.students.remove(student)
            student.course.remove_student(student)

            print("Student removed successfully!")
        else:
            print("Student not found!")

    def find_student(self, name):
        for student in self.students:
            if student.name == name:
                return student
        return None  

    def display_students(self):
        if self.students:
            for student in self.students:
                student.display()
                print()
        else:
            print("No students found")

    def update_mark(self, name, new_mark):
        student = self.find_student(name)

        if student:

            try:
                student.mark = new_mark
                print("Mark updated successfully!")
            except (ValueError, TypeError) as error:
                print(f"Error: {error}")

        else:
            print("Student not found")

    def student_count(self):
        return len(self.students)

    def find_by_course(self, course_code):
        course_student =[]

        for student in self.students:
            if student.course.course_code == course_code:
                course_student.append(student)

        return course_student

    def find_by_type(self, student_type):

        student_list = []

        for student in self.students:
            if student.student_type == student_type:
                student_list.append(student)
        return student_list
    
    def save_students(self, filename):
        with open(filename, "w") as file:
            saved_file = []
            for student in self.students:
                saved_file.append(student.to_dict())

            json.dump(saved_file, file, indent=4)

    def load_students(self, filename):

        try:
            with open(filename, "r") as file:    
                data = json.load(file)
        except FileNotFoundError:
            print("File does not exist!")
            self.students = []
            return []
        except json.JSONDecodeError:
            print("Invalid JSON!")
            self.students = []
            return[]

        loaded_students = []
        for student_data in data:
            try:

                if student_data["student_type"] == "Computer Science":
                    course = Course(student_data["course_name"],student_data["course_code"])
                    student = ComputerScienceStudent(
                        student_data["name"],
                        student_data["mark"],
                        student_data["age"],
                        student_data["programming_language"],
                        course
                    )
                    
                elif student_data["student_type"] == "Business":
                    course = Course(student_data["course_name"],student_data["course_code"])
                    student = BusinessStudent(
                        student_data["name"],
                        student_data["mark"],
                        student_data["age"],
                        student_data["specialisation"],
                        course
                    )

                else:
                    print(f"Unknown student type for "
                        f"{student_data['name']}. Skipping.")
                    continue

                course.add_student(student)
                loaded_students.append(student)

            except KeyError as error:
                print(f"Missing data in JSON: {error}."
                      f"Skipping student.")

        self.students = loaded_students

        return loaded_students

    def display_summary(self):
        print()
        print("=" * 10)
        print("Student Manager")
        print("=" * 10)

        print(
            f"Total Students: "
            f"{self.student_count()}"
        )

        print(
            f"Computer Science: "
            f"{len(self.find_by_type('Computer Science'))}"
        )

        print(
            f"Business: "
            f"{len(self.find_by_type('Business'))}"
        )
