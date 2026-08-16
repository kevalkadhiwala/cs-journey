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
