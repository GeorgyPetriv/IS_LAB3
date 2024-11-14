import random


class Group:
    def __init__(self, name, students_num):
        self.name = name
        self.students_num = students_num


class Lesson:

    def __init__(self, subject, lecturer, group, room, timeslot):
        self.subject = subject
        self.lecturer = lecturer
        self.group = group
        self.room = room
        self.timeslot = timeslot

    def __repr__(self):
        return f"({self.subject}, {self.lecturer}, {self.group.name}, {self.room.name}, {self.timeslot})"


class Room:
    def __init__(self, name, capacity):
        self.name = name
        self.capacity = capacity


class Subject:
    def __init__(self, name, teachers):
        self.name = name
        self.teachers = teachers

    def get_random_teacher(self):
        return random.choice(self.teachers)
