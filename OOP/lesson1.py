from abc import ABC, abstractmethod

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

        if isinstance(new_name, str) and new_name.strip():
            self._name = new_name.strip()
        elif not isinstance(new_name, str):
            raise ValueError("Name must be a string.")
        else:
            raise TypeError("Name cannot be empty.")
        
    @property
    def mark(self):
        return self._mark

    @mark.setter
    def mark(self, new_mark):
       
        if 0 <= new_mark <= 100: 
            self._mark = new_mark
        else:
            raise ValueError("Mark must be btw 0 and 100")
        
    @property
    def age(self):
        return self._age

    @age.setter
    def age(self, new_age):

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
        if 40 <= self._mark <= 100:
            return "passing!"
        
        elif 0 <= self._mark < 40:
            return "failing!"
        
        else:
            return "Invalid Marks!"       

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

##### Output
course1 = Course("Computer Science", "CSC101")
student1 = ComputerScienceStudent("Alice", 85, 20, "Python", course1)
course1.add_student(student1)

student2 = BusinessStudent("Bob", 72, 19, "Finance", course1)
course1.add_student(student2)

course1.remove_student(student1)
course1.display_students()