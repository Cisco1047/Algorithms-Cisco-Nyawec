class Dog:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def bark(self):
        print(f"Hello my name is {self.name} and I am {self.age} years old! and Woof Woof!")

if __name__ == "__main__":
    dog1 = Dog("Buddy", 3)
    dog1.bark()
    dog2 = Dog("Max", 5)
    dog2.bark()