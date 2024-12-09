import random
import numpy as np
import matplotlib.pyplot as plt


class Passenger:
    """
    Represents a passenger in an aircraft evacuation simulation.

    Attributes:
        base_time (float): Base evacuation time.
        panic_level (float): Passenger's panic level (0 to 1).
        baggage_delay (float): Delay caused by carrying baggage (0 to 1).
        age (str): Age category ('young' or 'old').
        move_time (float): Time taken to move per unit distance.
        row_speed_factor (float): Speed adjustment based on row location.
        exit_idx (int): Index of the assigned exit.
        distance_to_exit (int): Distance to the assigned exit.
        evacuation_time (float): Total calculated evacuation time.
    """
    def __init__(self, row_idx, row_speed_factor, exit_idx, age="young", emergency_level=1.0):
        """
        Initializes a Passenger object with evacuation-related characteristics.

        Args:
            row_idx (int): Row index of the passenger's seat.
            row_speed_factor (float): Speed factor for the passenger's row.
            exit_idx (int): Index of the assigned exit.
            age (str, optional): Age category. Defaults to "young".
            emergency_level (float, optional): Severity of emergency. Defaults to 1.0.
        """
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
        """
        Adjust panic level, baggage delay, and physical mobility based on the emergency level.

        Args:
            emergency_level (float): Emergency level (0 to 1).
        """
        self.panic_level *= emergency_level  # Panic level increases with emergency level
        self.panic_level = min(self.panic_level, 1)  # Cap at 1 for maximum panic level

        self.baggage_delay *= (1 - emergency_level * 0.5)  # Baggage delay decreases with higher emergency level

        # Physical mobility could increase as people are more urgent during high emergency levels
        self.move_time *= (1 - emergency_level * 0.2)  # Increase mobility as emergency level rises

    def calculate_evacuation_time(self):
        """
        Calculate the evacuation time considering the distance to exit and the row's speed factor.

        Returns:
            float: Total evacuation time.
        """
        return self.baggage_delay + ((self.panic_level) * self.move_time * self.row_speed_factor * self.distance_to_exit)


class Seat:
    """
        Represents a seat on the plane, which may be occupied by a passenger.

        Attributes:
            passenger (Passenger, optional): Passenger occupying the seat.
            row_idx (int): Index of the row containing this seat.
            row_speed_factor (float): Speed factor for the seat's row.
            exit_idx (int): Index of the nearest exit.
        """
    def __init__(self, row_idx, row_speed_factor, exit_idx):
        """
        Initializes a Seat object with its location and evacuation parameters.

        Args:
            row_idx (int): Index of the row containing this seat.
            row_speed_factor (float): Speed factor for the seat's row.
            exit_idx (int): Index of the nearest exit.
        """
        self.passenger = None
        self.row_idx = row_idx
        self.row_speed_factor = row_speed_factor
        self.exit_idx = exit_idx


class Row:
    """
        Represents a row of seats on the plane.

        Attributes:
            seats (list): List of Seat objects in this row.
            emergency_level (float): Emergency level affecting this row's evacuation.
        """
    def __init__(self, seats_per_row, row_idx, row_speed_factor, exits, emergency_level):
        """
        Initializes a Row object with a specified number of seats.

        Args:
            seats_per_row (int): Number of seats in this row.
            row_idx (int): Index of this row in the aircraft.
            row_speed_factor (float): Speed factor for this row.
            exits (list): List of available exit indices.
            emergency_level (float): Emergency severity level.
        """
        self.seats = [Seat(row_idx, row_speed_factor, self.assign_exit(row_idx, exits)) for _ in range(seats_per_row)]
        self.emergency_level = emergency_level

    def assign_exit(self, row_idx, exits):
        """
        Assign the nearest exit to the row.

        Args:
            row_idx (int): Index of the current row.
            exits (list): List of available exit indices.

        Returns:
            int: Index of the nearest exit to this row.
        """
        # Assign the nearest exit to the row
        return min(exits, key=lambda exit_idx: abs(exit_idx - row_idx))

    def evacuation_times(self):
        """
        Retrieve evacuation times for passengers in this row.

        Returns:
            list: Evacuation times for passengers in the row.
        """
        return [seat.passenger.evacuation_time for seat in self.seats if seat.passenger is not None]


class Plane:
    """
    Represents a plane with rows of seats and passengers.

    Attributes:
        rows (list): List of Row objects in the aircraft.
        exits (list): Indices of available exits.
        door_opening_time (int): Time for middle exit door to open.
        proportion_old (float): Proportion of elderly passengers.
        old_in_first_3_rows_prob (float): Probability of elderly passengers in first 3 rows.
        emergency_level (float): Severity of emergency situation.
        occupancy_rate (float): Fraction of seats occupied.
    """
    def __init__(self, rows, seats_per_row, exits, speed_factor=0.8, door_opening_time=2,
                 proportion_old=0.3, old_in_first_3_rows_prob=0.7, emergency_level=1.0, occupancy_rate=1.0):
        """
        Initializes a plane with a given number of rows, seats per row, exits, and optional blocked exit.
        Adds a speed factor for the first three rows and a door opening time for the middle exit.

        Args:
            rows (int): Total number of rows in the aircraft.
            seats_per_row (int): Number of seats in each row.
            exits (list): Indices of available exits.
            speed_factor (float, optional): Speed factor for first rows. Defaults to 0.8.
            door_opening_time (int, optional): Time for middle exit door. Defaults to 2.
            proportion_old (float, optional): Proportion of elderly passengers. Defaults to 0.3.
            old_in_first_3_rows_prob (float, optional): Probability of elderly in first rows. Defaults to 0.7.
            emergency_level (float, optional): Emergency severity. Defaults to 1.0.
            occupancy_rate (float, optional): Fraction of seats occupied. Defaults to 1.0.
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
        """
        Generates a list of passengers with their assigned nearest exit and age.
        Includes a higher probability for old passengers to sit in the first 3 rows.
        Only a proportion of seats are occupied based on the occupancy rate.

        Args:
            emergency_level (float): Emergency level

        Returns:
            list: List of tuples representing passenger data
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
        """
        Simulates the evacuation process considering bottlenecks, congestion, blocked exits, and door opening times.

        Returns:
            float: Average evacuation time for all passengers
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
    """
    Runs the Monte Carlo simulation for plane evacuation with a controlled occupancy rate.

    Returns:
        list: Evacuation times from all simulations
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