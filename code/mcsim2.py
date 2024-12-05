import random
import numpy as np
import matplotlib.pyplot as plt


class Passenger:
    def __init__(self, row_idx, row_speed_factor, exit_idx):
        self.base_time = random.uniform(2, 8)  # Base evacuation time (2-8 seconds)
        self.panic_level = random.uniform(0, 1)
        self.baggage_delay = random.uniform(0, 1)
        self.physical_mobility = random.uniform(1, 20)
        self.row_speed_factor = row_speed_factor  # Speed factor for the row
        self.exit_idx = exit_idx  # Assigned exit index
        self.distance_to_exit = abs(row_idx - exit_idx)  # Distance to the nearest exit
        self.evacuation_time = self.calculate_evacuation_time()

    def calculate_evacuation_time(self):
        # Calculate the evacuation time considering the distance to exit and the row's speed factor
        # return (self.base_time * (1 + self.panic_level + self.baggage_delay) * self.physical_mobility * self.row_speed_factor) + (self.distance_to_exit * 0.5)  # 0.5 is the speed factor for moving towards the exit
        return  self.baggage_delay + ((self.panic_level) * self.physical_mobility * self.row_speed_factor* self.distance_to_exit)  # 0.5 is the speed factor for moving towards the exit


class Seat:
    def __init__(self, row_idx, row_speed_factor, exit_idx):
        self.passenger = Passenger(row_idx, row_speed_factor, exit_idx)


class Row:
    def __init__(self, seats_per_row, row_idx, row_speed_factor, exits):
        self.seats = [Seat(row_idx, row_speed_factor, self.assign_exit(row_idx, exits)) for _ in range(seats_per_row)]

    def assign_exit(self, row_idx, exits):
        # Assign the nearest exit to the row
        return min(exits, key=lambda exit_idx: abs(exit_idx - row_idx))

    def evacuation_times(self):
        return [seat.passenger.evacuation_time for seat in self.seats]


class Plane:
    def __init__(self, rows, seats_per_row, exits, speed_factor=0.8, door_opening_time=2):
        """
        Initializes a plane with a given number of rows, seats per row, exits, and optional blocked exit.
        Adds a speed factor for the first three rows and a door opening time for the middle exit.
        """
        self.rows = [Row(seats_per_row, idx, speed_factor if idx < 3 else 1, exits) for idx in range(rows)]  # Apply speed factor to first 3 rows
        self.exits = exits
        self.door_opening_time = door_opening_time  # Time for middle exit door to open
        self.line = self.generate_line()

    def generate_line(self):
        """
        Generates a list of passengers with their assigned nearest exit.
        """
        line = []
        for row_idx, row in enumerate(self.rows):
            for evac_time in row.evacuation_times():
                # Assign passenger to the nearest exit
                nearest_exit = min(self.exits, key=lambda exit_idx: abs(exit_idx - row_idx))
                line.append((row_idx, nearest_exit, evac_time))
        return line

    def simulate_evacuation(self):
        """
        Simulates the evacuation process considering bottlenecks, congestion, blocked exits, and door opening times.
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


def monte_carlo_simulation(rows=30, seats_per_row=6, exits=[0, 15, 29], speed_factor=0.8, door_opening_time=2, num_simulations=1000):
    """
    Runs the Monte Carlo simulation for plane evacuation.

    Parameters:
        rows (int): Number of rows in the plane.
        seats_per_row (int): Number of seats per row.
        exits (list): List of exit row indices.
        speed_factor (float): Speed factor for the first 3 rows (default 0.8).
        door_opening_time (int): Time for the middle exit door to open (default 2 seconds).
        num_simulations (int): Number of Monte Carlo simulations to run.

    Returns:
        evacuation_times (list): List of total evacuation times from all simulations.
    """
    evacuation_times = []
    for _ in range(num_simulations):
        plane = Plane(rows, seats_per_row, exits, speed_factor, door_opening_time)
        evacuation_times.append(plane.simulate_evacuation())
    return evacuation_times


# Run the simulation
def main():
    rows = 30           # Number of rows in the plane
    seats_per_row = 6   # Seats per row (standard economy configuration)
    exits = [0, 15, 29] # Locations of exits (front, middle, back exits)
    speed_factor = 0.8  # First three rows move faster (80% of the normal time)
    door_opening_time = 2  # Time for middle exit door to open (2 seconds)
    num_simulations = 1000

    evacuation_times = monte_carlo_simulation(rows, seats_per_row, exits, speed_factor, door_opening_time, num_simulations)

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
