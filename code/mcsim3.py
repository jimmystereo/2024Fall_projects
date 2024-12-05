import random
import numpy as np
import matplotlib.pyplot as plt


class Passenger:
    """
    Represents a passenger with a position and evacuation characteristics.

    Attributes:
        row (int): Current row of the passenger.
        seat (int): Seat position (e.g., aisle=0, window=1, etc.).
        exit_row (int): Row of the assigned exit.
        panic_level (float): Panic level between 0 and 1, affecting evacuation speed.
        baggage_delay (float): Delay caused by handling baggage, between 0 and 1.
        physical_mobility (float): Speed factor between 0.5 (slow) and 1.5 (fast).
        evacuation_time (float): Time taken for the passenger to evacuate.
        has_evacuated (bool): Whether the passenger has reached the exit.

    Methods:
        calculate_base_time():
            Calculates the base time for evacuation based on panic, baggage, and mobility.
        move_toward_exit(aisle_occupancy):
            Moves the passenger one step closer to the exit if the aisle is free.
    """

    def __init__(self, row, seat, exit_row, panic_level, baggage_delay, physical_mobility):
        """
        Initializes a Passenger object.

        Args:
            row (int): Starting row of the passenger.
            seat (int): Seat position in the row.
            exit_row (int): Row of the assigned exit.
            panic_level (float): Panic level affecting evacuation time.
            baggage_delay (float): Delay caused by baggage handling.
            physical_mobility (float): Speed factor for movement.

        >>> passenger = Passenger(5, 1, 0, 0.2, 0.1, 1.0)
        >>> passenger.row
        5
        >>> passenger.exit_row
        0
        >>> passenger.has_evacuated
        False
        """
        self.row = row
        self.seat = seat
        self.exit_row = exit_row
        self.panic_level = panic_level
        self.baggage_delay = baggage_delay
        self.physical_mobility = physical_mobility
        self.evacuation_time = self.calculate_base_time()
        self.has_evacuated = False

    def calculate_base_time(self):
        """
        Calculates the base time it takes to evacuate from the seat.

        Returns:
            float: Base evacuation time in seconds.

        >>> passenger = Passenger(5, 1, 0, 0.2, 0.1, 1.0)
        >>> 2 <= passenger.calculate_base_time() <= 6  # Random factor included
        True
        """
        base_time = random.uniform(2, 4)  # Time to unbuckle seatbelt and stand up
        delay = (1 + self.panic_level + self.baggage_delay) * self.physical_mobility
        return base_time * delay

    def move_toward_exit(self, aisle_occupancy):
        """
        Moves the passenger one step closer to their exit if possible.

        Args:
            aisle_occupancy (list): Aisle occupancy status by row.

        >>> passenger = Passenger(5, 1, 0, 0.2, 0.1, 1.0)
        >>> aisle_occupancy = [0] * 30
        >>> passenger.move_toward_exit(aisle_occupancy)
        >>> passenger.row
        4
        """
        if not self.has_evacuated:
            if aisle_occupancy[self.row] == 0:  # Aisle is free at current row
                self.row += np.sign(self.exit_row - self.row)  # Move toward exit row
                self.evacuation_time += 1  # Add 1 second per step
            if self.row == self.exit_row:  # Reached the exit
                self.has_evacuated = True


class Plane:
    """
    Represents the plane as a spatial grid with passengers and exits.

    Attributes:
        rows (int): Number of rows in the plane.
        seats_per_row (int): Number of seats per row.
        exits (list): List of exit row indices.
        passengers (list): List of Passenger objects.
        aisle_occupancy (list): Current aisle occupancy status.

    Methods:
        create_passengers():
            Initializes the passengers with random attributes.
        simulate_evacuation():
            Simulates the evacuation step by step and returns the total time.
    """

    def __init__(self, rows, seats_per_row, exits):
        """
        Initializes a Plane object with passengers and exits.

        Args:
            rows (int): Number of rows in the plane.
            seats_per_row (int): Number of seats per row.
            exits (list): Row indices of the exits.

        >>> plane = Plane(30, 6, [0, 29])
        >>> len(plane.passengers)
        180
        """
        self.rows = rows
        self.seats_per_row = seats_per_row
        self.exits = exits
        self.passengers = self.create_passengers()
        self.aisle_occupancy = [0] * rows  # 0 = aisle free, 1 = occupied

    def create_passengers(self):
        """
        Creates passengers, assigning them to seats and exits.

        Returns:
            list: List of Passenger objects.

        >>> plane = Plane(30, 6, [0, 29])
        >>> len(plane.create_passengers())
        180
        """
        passengers = []
        for row in range(self.rows):
            for seat in range(self.seats_per_row):
                # Assign each passenger to the nearest exit
                exit_row = min(self.exits, key=lambda x: abs(x - row))
                passengers.append(Passenger(
                    row=row,
                    seat=seat,
                    exit_row=exit_row,
                    panic_level=random.uniform(0, 1),
                    baggage_delay=random.uniform(0, 1),
                    physical_mobility=random.uniform(0.5, 1.5)
                ))
        return passengers

    def simulate_evacuation(self):
        """
        Simulates the evacuation step by step.

        Returns:
            int: Total evacuation time in seconds.

        >>> plane = Plane(10, 4, [0, 9])
        >>> 10 <= plane.simulate_evacuation() <= 300  # Random simulation
        True
        """
        total_time = 0
        while not all(p.has_evacuated for p in self.passengers):
            # Update aisle occupancy
            self.aisle_occupancy = [0] * self.rows
            for p in self.passengers:
                if not p.has_evacuated:
                    self.aisle_occupancy[p.row] = 1  # Mark aisle as occupied at this row

            # Move passengers one step toward their exits
            for p in self.passengers:
                p.move_toward_exit(self.aisle_occupancy)

            total_time += 1

        return total_time


def monte_carlo_simulation(rows=30, seats_per_row=6, exits=[0, 29], num_simulations=100):
    """
    Runs the Monte Carlo simulation for plane evacuation with spatial movement.

    Args:
        rows (int): Number of rows in the plane.
        seats_per_row (int): Number of seats per row.
        exits (list): List of exit row indices.
        num_simulations (int): Number of simulations to run.

    Returns:
        list: List of evacuation times for each simulation.

    >>> evacuation_times = monte_carlo_simulation(10, 4, [0, 9], 5)
    >>> len(evacuation_times)
    5
    >>> all(10 <= t <= 300 for t in evacuation_times)  # Random range
    True
    """
    evacuation_times = []
    for _ in range(num_simulations):
        plane = Plane(rows, seats_per_row, exits)
        evacuation_times.append(plane.simulate_evacuation())
    return evacuation_times

