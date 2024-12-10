import random
from row import Row
from passenger import Passenger


class Plane:
    """Represents a plane with rows of seats and passengers.

    Attributes:
        rows (list): List of Row objects in the aircraft
        exits (list): Indices of available exits
        door_opening_time (float): Time for the middle exit door to open
        proportion_old (float): Proportion of elderly passengers
        old_in_first_3_rows_prob (float): Probability of elderly passengers sitting in the first 3 rows
        emergency_level (float): Severity of the emergency situation
        occupancy_rate (float): Fraction of seats occupied

    :param rows: Number of rows in the aircraft
    :param seats_per_row: Number of seats per row
    :param exits: Indices of available exits
    :param speed_factor: Speed adjustment factor for the first three rows
    :param door_opening_time: Time (in seconds) for the middle exit door to open
    :param proportion_old: Proportion of elderly passengers
    :param old_in_first_3_rows_prob: Probability of elderly passengers sitting in the first 3 rows
    :param emergency_level: Severity of the emergency situation (0 to 1)
    :param occupancy_rate: Fraction of seats occupied

    >>> plane = Plane(rows=10, seats_per_row=6, exits=[0, 15, 29])
    >>> len(plane.rows) == 10
    True
    >>> all(len(row.seats) == (2 if i < 3 else 6) for i, row in enumerate(plane.rows))
    True
    >>> plane = Plane(rows=10, seats_per_row=6, exits=[0, 15], occupancy_rate=0.5)
    >>> all(0 < len(row.seats) <= 6 for row in plane.rows)
    True
    """
    def __init__(self, rows, seats_per_row, exits, speed_factor=0.8, door_opening_time=2,
                 proportion_old=0.3, old_in_first_3_rows_prob=0.7, emergency_level=1.0, occupancy_rate=1.0):
        """Initializes a plane with a given number of rows, seats per row, exits, and optional blocked exit.
        Adds a speed factor for the first three rows and a door opening time for the middle exit.
        """
        self.proportion_old = proportion_old  # Proportion of old passengers
        self.old_in_first_3_rows_prob = old_in_first_3_rows_prob  # Probability that old passengers sit in the first 3 rows
        self.rows = []
        self.exits = exits
        self.door_opening_time = door_opening_time  # Time for middle exit door to open
        self.emergency_level = emergency_level  # Emergency level
        self.occupancy_rate = occupancy_rate  # Fraction of seats occupied

        # Adjust seats per row for the first three rows
        for idx in range(rows):
            current_seats_per_row = 2 if idx < 3 else seats_per_row
            self.rows.append(Row(current_seats_per_row, idx, speed_factor if idx < 3 else 1, exits, emergency_level))

        self.line = self.generate_line(emergency_level)

    def generate_line(self, emergency_level):
        """Generates a list of passengers with their assigned nearest exit and age.
        Includes a higher probability for old passengers to sit in the first 3 rows.
        Only a proportion of seats are occupied based on the occupancy rate.

        :param emergency_level: Emergency level

        :return: List of tuples representing passenger data
        """
        line = []
        for row_idx, row in enumerate(self.rows):
            for seat in row.seats:
                # Only add passengers to seats based on occupancy rate
                if random.random() > self.occupancy_rate:
                    continue  # Skip this seat as it's unoccupied

                # Randomly assign 'young' or 'old' based on the given proportion
                age = 'old' if random.random() < self.proportion_old else 'young'

                # Adjust the row assignment for old passengers
                if age == 'old' and random.random() < self.old_in_first_3_rows_prob:
                    # Assign old passengers to the first 3 rows with higher probability
                    row_idx = min(row_idx, 2)  # Limit row index to 0, 1, 2 (first three rows)

                passenger = Passenger(row_idx, seat.row_speed_factor, seat.exit_idx, age, emergency_level)
                evac_time = passenger.evacuation_time
                nearest_exit = min(self.exits, key=lambda exit_idx: abs(exit_idx - row_idx))
                line.append((row_idx, nearest_exit, evac_time))
        return line


    def simulate_evacuation(self):
        """Simulates the evacuation process considering bottlenecks, congestion, blocked exits, and door opening times.

        :return: Average evacuation time for all passengers

        >>> plane = Plane(rows=30, seats_per_row=6, exits=[0, 15, 29])
        >>> plane.simulate_evacuation() > 0
        True
        >>> plane = Plane(rows=10, seats_per_row=6, exits=[0, 15], emergency_level=0.8, proportion_old=0.4)
        >>> plane.simulate_evacuation() > 0
        True
        """
        exit_queues = {exit_idx: [] for exit_idx in self.exits}
        aisle_congestion_factor = random.uniform(1, 1.5)

        # Assign passengers to exit queues, excluding the blocked exit
        for row_idx, exit_idx, evac_time in self.line:
            exit_queues[exit_idx].append((row_idx, evac_time))

        # Simulate evacuation at each exit
        total_time = 0
        for exit_idx, queue in exit_queues.items():
            max_exit_time = 0
            for passenger_idx, (_, evac_time) in enumerate(queue):
                # Add delays caused by aisle congestion and bottlenecks
                evac_time *= aisle_congestion_factor
                if passenger_idx > 0:
                    max_exit_time = max(max_exit_time, queue[passenger_idx - 1][1] + 3)
                else:
                    max_exit_time = evac_time
                total_time += max_exit_time

        # Add door opening time for the middle exit (if not blocked)
        if 15 in self.exits:
            total_time += self.door_opening_time

        return total_time / len(self.line)
