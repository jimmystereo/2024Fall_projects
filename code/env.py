import numpy as np


class Passenger:
    def __init__(self):
        self.name = None
        self.type = None
        self.speed = None
        self.status = "inside"
        pass

class Seat:
    def __init__(self):
        self.passenger = None
        pass


class Plane:
    def __init__(self, length, width):
        self.length = length
        self.width = width
        self.seats = self.generate_seats()


    def generate_seats(self):
        seats = np.array([[Seat() for i in range(self.width)] for j in range(self.length)])
        return seats

p = Plane(20, 30)
p.seats[0,0].passenger

from random import randint
time = 0
line = []
for i in range(10):
    line.append(randint(1, 10))
max_time = 0
for i in range(len(line)):
    if line[i] < max_time:
        line[i] = max_time
    else:
        max_time = line[i]
for i in range(len(line)):
    time += i*line[i]

time/10