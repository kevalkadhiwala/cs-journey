class Student:

    def __init__(self, name, mark, age):
        self.name = name
        self.mark = mark
        self.age = age

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

    def __str__(self):
        return f"Student(name={self.name}, age={self.age}, mark={self._mark})"

student1 = Student("Alice", 85, 20)
student1.mark = 95
student1.age = 21
student1.name = "Charlie"

student1.display()