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
# p.generate_seats()

p.seats[0,0].passenger