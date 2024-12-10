import random
import numpy as np
import matplotlib.pyplot as plt


class Passenger:
    """Represents a passenger in an aircraft evacuation simulation.

    Attributes:
        base_time (float): Base evacuation time
        panic_level (float): Passenger's panic level (0 to 1)
        baggage_delay (float): Delay caused by carrying baggage (0 to 1)
        age (str): Age category, either 'young' or 'old'
        move_time (float): Time taken to move per unit distance
        row_speed_factor (float): Speed adjustment factor for the passenger's row
        exit_idx (int): Index of the assigned exit
        distance_to_exit (int): Distance to the assigned exit
        evacuation_time (float): Total calculated evacuation time

    :param row_idx: Index of the passenger's seat row
    :param age: Age category ('young' or 'old')
    :param row_speed_factor: Speed adjustment based on row location
    :param exit_idx: Index of the assigned exit
    :param emergency_level: Optional. Emergency level affecting passenger behavior (0 to 1). Defaults to 1.0

    >>> # Test initialization
    >>> p = Passenger(row_idx=5, row_speed_factor=0.8, exit_idx=10, age="young", emergency_level=1.0)
    >>> isinstance(p, Passenger)
    True
    >>> p.evacuation_time > 0 # Evacuation time is always positive
    True

    >>> # Test evacuation time differences between young and old
    >>> py = Passenger(row_idx=5, row_speed_factor=1.0, exit_idx=10, age="young")
    >>> po = Passenger(row_idx=5, row_speed_factor=1.0, exit_idx=10, age="old")
    >>> po.move_time > py.move_time # Old passengers should take longer to move
    True
    """
    def __init__(self, row_idx, row_speed_factor, exit_idx, age="young", emergency_level=1.0):
        """Initializes a Passenger object with evacuation-related characteristics."""
        self.base_time = random.uniform(2, 8)  # Base evacuation time (2-8 seconds)
        self.panic_level = random.uniform(0, 1)
        self.baggage_delay = random.uniform(0, 1)
        self.age = age

        # Adjust physical mobility based on age
        if self.age == 'old':
            self.move_time = random.uniform(8, 10)  # Older passengers are less mobile
        else:
            self.move_time = random.uniform(1, 4)  # Younger passengers are more mobile

        self.row_speed_factor = row_speed_factor  # Speed factor for the row
        self.exit_idx = exit_idx  # Assigned exit index
        self.distance_to_exit = abs(row_idx - exit_idx)  # Distance to the nearest exit

        # Apply emergency level adjustments
        self.apply_emergency_level(emergency_level)

        # Calculate evacuation time
        self.evacuation_time = self.calculate_evacuation_time()

    def apply_emergency_level(self, emergency_level):
        """Adjust panic level, baggage delay, and physical mobility based on the emergency level.

        :param emergency_level: Emergency level affecting passenger behavior (0 to 1)

        >>> p = Passenger(row_idx=5, row_speed_factor=0.8, exit_idx=10, emergency_level=0.5)
        >>> init_panic = p.panic_level
        >>> init_move_time = p.move_time
        >>> p.apply_emergency_level(0.5)
        >>> 0 <= p.panic_level <= 1
        True
        >>> 0 <= p.move_time < init_move_time
        True
        """
        self.panic_level *= emergency_level  # Panic level increases with emergency level
        self.panic_level = min(self.panic_level, 1)  # Cap at 1 for maximum panic level

        self.baggage_delay *= (1 - emergency_level * 0.5)  # Baggage delay decreases with higher emergency level

        # Physical mobility could increase as people are more urgent during high emergency levels
        self.move_time *= (1 - emergency_level * 0.2)  # Increase mobility as emergency level rises

    def calculate_evacuation_time(self):
        """Calculate the evacuation time considering the distance to exit and the row's speed factor.

        :return: Total evacuation time

        >>> p = Passenger(row_idx=5, row_speed_factor=0.8, exit_idx=10)
        >>> p.calculate_evacuation_time() > 0
        True
        >>> p_near = Passenger(row_idx=5, row_speed_factor=1.0, exit_idx=6)
        >>> p_far = Passenger(row_idx=5, row_speed_factor=1.0, exit_idx=25)
        >>> p_near.calculate_evacuation_time() < p_far.calculate_evacuation_time()
        True
        """
        return self.baggage_delay + ((self.panic_level) * self.move_time * self.row_speed_factor * self.distance_to_exit)


class Seat:
    """Represents a seat on the plane, which may be occupied by a passenger.

    Attributes:
        passenger (Passenger): Optional. Passenger occupying the seat

    :param row_idx: Index of the row containing this seat
    :param row_speed_factor: Speed factor for the seat's row
    :param exit_idx: Index of the nearest exit

    >>> seat = Seat(row_idx=5, row_speed_factor=1.0, exit_idx=10)
    >>> isinstance(seat, Seat)
    True
    """
    def __init__(self, row_idx, row_speed_factor, exit_idx):
        """Initializes a Seat object with its location and evacuation parameters."""
        self.passenger = None
        self.row_idx = row_idx
        self.row_speed_factor = row_speed_factor
        self.exit_idx = exit_idx


class Row:
    """Represents a row of seats on the plane.

    Attributes:
        seats (list): List of Seat objects in this row
        emergency_level (float): Emergency level affecting the row's evacuation

    :param seats_per_row: Number of seats in this row
    :param row_idx: Index of this row
    :param row_speed_factor: Speed adjustment factor for passengers in this row
    :param exits: List of indices of available exits
    :param emergency_level: Emergency level affecting this row's evacuation

    >>> r = Row(seats_per_row=6, row_idx=5, row_speed_factor=1.0, exits=[0, 15, 29], emergency_level=1.0)
    >>> len(r.seats) == 6
    True
    >>> all(isinstance(seat, Seat) for seat in r.seats)
    True
    """
    def __init__(self, seats_per_row, row_idx, row_speed_factor, exits, emergency_level):
        """Initializes a Row object with a specified number of seats."""
        self.seats = [Seat(row_idx, row_speed_factor, self.assign_exit(row_idx, exits)) for _ in range(seats_per_row)]
        self.emergency_level = emergency_level

    def assign_exit(self, row_idx, exits):
        """Assign the nearest exit to the row.

        :param row_idx: ndex of the current row
        :param exits: List of available exit indices

        :return: Index of the nearest exit to this row

        >>> row = Row(seats_per_row=6, row_idx=5, row_speed_factor=1.0, exits=[0, 15, 29], emergency_level=1.0)
        >>> row.assign_exit(5, [0, 15, 29]) in [0, 15, 29]
        True
        >>> row.assign_exit(13, [0, 15, 29]) == 15
        True
        >>> row.assign_exit(0, [0, 15, 29]) == 0
        True
        >>> row.assign_exit(29, [0, 15, 29]) == 29
        True
        """
        # Assign the nearest exit to the row
        return min(exits, key=lambda exit_idx: abs(exit_idx - row_idx))

    def evacuation_times(self):
        """Retrieve evacuation times for passengers in this row.

        :return: Evacuation times for passengers in the row

        >>> r = Row(seats_per_row=6, row_idx=5, row_speed_factor=1.0, exits=[0, 15, 29], emergency_level=1.0)
        >>> all(isinstance(time, float) for time in r.evacuation_times())
        True
        """
        return [seat.passenger.evacuation_time for seat in self.seats if seat.passenger is not None]


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


def monte_carlo_simulation(rows=30, seats_per_row=6, exits=[0, 15, 29], speed_factor=0.8, door_opening_time=2,
                           num_simulations=1000, proportion_old=0.3, old_in_first_3_rows_prob=0.7,
                           emergency_level=1.0, occupancy_rate=1.0):
    """Runs the Monte Carlo simulation for plane evacuation with a controlled occupancy rate.

    :return: Evacuation times from all simulations

    >>> times = monte_carlo_simulation(rows=10, seats_per_row=6, num_simulations=100, exits=[0, 15])
    >>> len(times) == 100
    True
    >>> all(time > 0 for time in times)
    True
    >>> np.mean(times) > 0
    True
    >>> 0 < np.std(times) < 50
    True
    """
    evacuation_times = []
    for _ in range(num_simulations):
        plane = Plane(rows, seats_per_row, exits, speed_factor, door_opening_time, proportion_old,
                      old_in_first_3_rows_prob, emergency_level, occupancy_rate)
        evacuation_times.append(plane.simulate_evacuation())
    return evacuation_times

def main():
    rows = 30           # Number of rows in the plane
    seats_per_row = 6   # Seats per row (standard economy configuration)
    exits = [0, 15, 29] # Locations of exits (front, middle, back exits)
    speed_factor = 0.6  # First three rows move faster (80% of the normal time)
    door_opening_time = 2  # Time for middle exit door to open (2 seconds)
    num_simulations = 1000
    proportion_old = 0.3  # 30% old passengers
    old_in_first_3_rows_prob = 0.6  # 70% chance for old passengers to sit in the first 3 rows
    emergency_level = 0.9  # Emergency level: 0.0 (low) to 1.0 (high)
    occupancy_rate = 0.8  # 80% of seats are occupied

    evacuation_times = monte_carlo_simulation(rows, seats_per_row, exits, speed_factor, door_opening_time, num_simulations,
                                              proportion_old, old_in_first_3_rows_prob, emergency_level, occupancy_rate)

    # Analyze the results
    average_time = np.mean(evacuation_times)
    std_deviation = np.std(evacuation_times)

    print(f"Average evacuation time: {average_time:.2f} seconds")
    print(f"Standard deviation: {std_deviation:.2f} seconds")

    # Plot the results
    plt.hist(evacuation_times, bins=30, color='orange', alpha=0.7, edgecolor='black')
    plt.title('Distribution of Evacuation Times')
    plt.xlabel('Evacuation Time (seconds)')
    plt.ylabel('Frequency')
    plt.show()


if __name__ == "__main__":
    main()