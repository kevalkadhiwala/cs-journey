from abc import ABC, abstractmethod
import json

# ============================================================
# STUDENT
# ============================================================

class Student(ABC):

    def __init__(self, name, mark, age, course):
        self.name = name
        self.mark = mark
        self.age = age
        self.course = course

    @property
    def name(self):
        return self._name
    
    @name.setter
    def name(self, new_name):

        # TypeError is more appropriate for wrong type
        if not isinstance(new_name, str):
            raise TypeError("Name must be a string.")

        # ValueError is appropriate for an empty string
        if not new_name.strip():
            raise ValueError("Name cannot be empty.")

        self._name = new_name.strip()
        
    @property
    def mark(self):
        return self._mark

    @mark.setter
    def mark(self, new_mark):

        if not isinstance(new_mark, (int, float)):
            raise TypeError("Mark must be a number.")
    
        if 0 <= new_mark <= 100: 
            self._mark = new_mark
        else:
            raise ValueError("Mark must be btw 0 and 100")
        
    @property
    def age(self):
        return self._age

    @age.setter
    def age(self, new_age):

        if not isinstance(new_age, int):
            raise TypeError("Age must be an integer.")

        if 0 < new_age:
            self._age = new_age

        else:
            raise ValueError("Age must be greater than 0.") 

    @abstractmethod
    def course_info(self):
        pass   

    @property
    @abstractmethod
    def student_type(self):
        pass

    def introduce(self):
        print(f"Hi, my name is {self.name}.")

    def is_passing(self):
        return self._mark >= 40
    
    def get_grade(self):
        if 70 <= self._mark <= 100:
            return "A" 

        elif 60 <= self._mark <= 69:
            return "B" 

        elif 50 <= self._mark <= 59:
            return "C" 

        elif 40 <= self._mark <= 49:
            return "D" 

        elif 0 <= self._mark <= 39:
            return "F"

        else:
            return "Invalid marks!" 

    def get_status(self):
        if 40 <= self._mark:
            return "passing!"
        
        return "failing!"
        
    def __eq__(self, other):
        return isinstance(other, Student) and self.name == other.name

    def __repr__(self):
        return f"Student(name={self.name}, age={self.age}, mark={self.mark})"

    def to_dict(self):
        return {"name": self.name, "mark": self.mark, "age": self.age, "student_type": self.student_type, "course_name": self.course.course_name, "course_code": self.course.course_code}

    def save_students(self, filename):
        pass

    def display(self):
        print(f"Name: {self.name}")
        print(f"Mark: {self.mark}")
        print(f"Age: {self.age}")
        print(f"Grade: {self.get_grade()}")
        self.course.display()

    def __str__(self):
        return f"Student(name={self.name}, age={self.age}, mark={self._mark})"

####
class ComputerScienceStudent(Student):
    
    def __init__(self, name, mark, age, programming_language, course):
        super().__init__(name, mark, age, course)
        self.programming_language = programming_language

    @property
    def programming_language(self):
        return self._programming_language
    
    @programming_language.setter
    def programming_language(self, new_language):
        self._programming_language = new_language

    def course_info(self):
        return f"{self.name} studies Computer Science using {self.programming_language}."

    @property
    def student_type(self):
        return "Computer Science"

    def __repr__(self):
        return f"Student(name={self.name}, mark={self.mark}, language={self.programming_language})"

    def to_dict(self):
        data = super().to_dict()
        data["programming_language"] = self.programming_language
        return data
    
    def display(self):
        super().display()
        print(f"Programming Language: {self.programming_language}")

#####
class BusinessStudent(Student):
    
    def __init__(self, name, mark, age, specialisation, course):
        super().__init__(name, mark, age, course)
        self.specialisation = specialisation

    @property
    def specialisation(self):
        return self._specialisation
    
    @specialisation.setter
    def specialisation(self, new_specialisation):
        self._specialisation = new_specialisation

    def course_info(self):
        return f"{self.name} studies Business specialising in {self.specialisation}."

    @property
    def student_type(self):
        return "Business"

    def __repr__(self):
        return f"Student(name={self.name}, mark={self.mark}, specialisation={self.specialisation})"

    def to_dict(self):
        data = super().to_dict()
        data["specialisation"] = self.specialisation
        return data

    def display(self):
        super().display()
        print(f"Specialisation: {self.specialisation}")

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
        if student in self.students:
            self.students.remove(student)
            print("Student removed successfully!")
        else:
            print("Student is not Enrolled!")         

    def display(self):
        print(f"Course: {self.course_name}")
        print(f"Code: {self.course_code}")


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


# ============================================================
# INPUT VALIDATION FUNCTIONS
# ============================================================
# Moved validation into separate functions.
# This keeps the main menu much cleaner.

def get_valid_mark():

    while True:

        try:

            mark = int(input("Enter mark: "))

            if 0 <= mark <= 100:

                return mark

            print("Mark must be between 0 and 100.")

        except ValueError:

            print("Enter a valid number!")

def get_valid_age():

    while True:

        try:

            age = int(input("Enter age: "))

            if age > 0:

                return age

            print("Age must be greater than 0.")

        except ValueError:

            print("Enter a valid number!")


def get_student_type():

    while True:

        student_type = input(
            "Enter student type "
            "(1. Computer Science / 2. Business): "
        )

        if student_type in ["1", "2"]:

            return student_type

        print("Invalid student type!")


def get_menu_choice():

    valid_choices = [
        "1", "2", "3",
        "4", "5", "6",
        "7", "8", "9"
    ]

# ============================================================
# MENU
# ============================================================
  
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


# ============================================================
# MAIN PROGRAM
# ============================================================

manager = StudentManager()

manager.load_students("student.json")

while True:
    display_menu()

    choice = get_menu_choice()

    if choice == "9":
        save_choice = input(
            "Save changes before exiting? (y/n): "
        ).lower()

        if save_choice == "y":

            manager.save_students("students.json")

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
        manager.save_students("students.json")


##### Output

course1 = Course("Computer Science", "CSC101")
student1 = ComputerScienceStudent("Alice", 85, 20, "Python", course1)
student2 = BusinessStudent("Bob", 72, 19, "Finance", course1)

manager = StudentManager()

manager.load_students("students.json")

