from random import randint

class Passenger:
    """
    Represents a passenger with a random evacuation time.
    """
    def __init__(self):
        # Evacuation time is randomly assigned between 1 and 10 seconds
        self.evacuation_time = randint(1, 10)


class Seat:
    """
    Represents a seat occupied by a passenger.
    """
    def __init__(self):
        self.passenger = Passenger()


class Row:
    """
    Represents a row of seats in the plane.
    """
    def __init__(self, seats_per_row):
        self.seats = [Seat() for _ in range(seats_per_row)]

    def evacuation_times(self):
        """
        Returns the evacuation times of all passengers in this row.
        """
        return [seat.passenger.evacuation_time for seat in self.seats]


class Plane:
    """
    Represents the entire plane, consisting of multiple rows.
    """
    def __init__(self, rows, seats_per_row):
        self.rows = [Row(seats_per_row) for _ in range(rows)]
        self.line = self.generate_line()

    def generate_line(self):
        """
        Creates a queue (line) of passengers by flattening all rows into a list.
        """
        line = []
        for row in self.rows:
            line.extend(row.evacuation_times())
        return line

    def simulate_evacuation(self):
        """
        Simulates the evacuation process and calculates the average evacuation time.
        """
        line = self.line[:]
        max_time = 0
        total_time = 0

        for i in range(len(line)):
            if line[i] < max_time:
                line[i] = max_time
            else:
                max_time = line[i]

        for i in range(len(line)):
            total_time += i * line[i]

        return total_time / len(line)


# Run the simulation
def main():
    rows = 10       # Number of rows in the plane
    seats_per_row = 6  # Seats per row

    plane = Plane(rows, seats_per_row)
    average_time = plane.simulate_evacuation()

    print(f"Average evacuation time per passenger: {average_time:.2f} seconds")


if __name__ == "__main__":
    main()
