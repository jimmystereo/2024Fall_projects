import random
import numpy as np


class Passenger:
    """
    Represents a passenger with unique attributes affecting evacuation speed.
    """
    def __init__(self, panic_level=0.5, baggage_delay=0.5):
        # Base evacuation time (e.g., between 2 and 8 seconds)
        self.base_time = random.uniform(2, 8)
        # Panic level increases evacuation time (e.g., 0 = calm, 1 = panicked)
        self.panic_level = panic_level
        # Baggage delay factor (e.g., 0 = no baggage, 1 = heavy baggage)
        self.baggage_delay = baggage_delay
        # Total evacuation time for this passenger
        self.evacuation_time = self.calculate_evacuation_time()

    def calculate_evacuation_time(self):
        """
        Calculates the evacuation time based on attributes.
        """
        return self.base_time * (1 + self.panic_level + self.baggage_delay)


class Seat:
    """
    Represents a seat occupied by a passenger.
    """
    def __init__(self):
        self.passenger = Passenger(
            panic_level=random.uniform(0, 1), baggage_delay=random.uniform(0, 1)
        )


class Row:
    """
    Represents a row of seats in the plane.
    """
    def __init__(self, seats_per_row):
        self.seats = [Seat() for _ in range(seats_per_row)]

    def evacuation_times(self):
        """
        Returns the evacuation times of all passengers in the row.
        """
        return [seat.passenger.evacuation_time for seat in self.seats]


class Plane:
    """
    Represents the entire plane, consisting of multiple rows and exits.
    """
    def __init__(self, rows, seats_per_row, exits):
        self.rows = [Row(seats_per_row) for _ in range(rows)]
        self.exits = exits  # List of exit locations (row indices)
        self.line = self.generate_line()

    def generate_line(self):
        """
        Creates a queue (line) of passengers by flattening all rows into a list.
        Assigns passengers to the nearest exit.
        """
        line = []
        for row_idx, row in enumerate(self.rows):
            for evacuation_time in row.evacuation_times():
                # Find the nearest exit for the passenger
                nearest_exit = min(self.exits, key=lambda exit_idx: abs(exit_idx - row_idx))
                line.append((row_idx, nearest_exit, evacuation_time))
        return line

    def simulate_evacuation(self):
        """
        Simulates the evacuation process with bottlenecks and multiple exits.
        """
        exit_queues = {exit_idx: [] for exit_idx in self.exits}  # Passengers per exit

        # Assign passengers to exit queues
        for row_idx, exit_idx, evac_time in self.line:
            exit_queues[exit_idx].append((row_idx, evac_time))

        # Sort passengers in each exit queue by their evacuation times
        for exit_idx in exit_queues:
            exit_queues[exit_idx].sort(key=lambda x: x[1])  # Sort by evacuation time

        # Simulate evacuation at each exit
        total_time = 0
        for exit_idx, queue in exit_queues.items():
            max_exit_time = 0
            for passenger_idx, (_, evac_time) in enumerate(queue):
                # Add delays caused by bottlenecks (e.g., limit of 1 passenger every 3 seconds)
                if passenger_idx > 0:
                    max_exit_time = max(max_exit_time, queue[passenger_idx - 1][1] + 3)
                else:
                    max_exit_time = evac_time
                total_time += max_exit_time

        return total_time / len(self.line)


def monte_carlo_simulation(rows=30, seats_per_row=6, exits=[0, 29], num_simulations=1000):
    """
    Runs the Monte Carlo simulation for plane evacuation.

    Parameters:
        rows (int): Number of rows in the plane.
        seats_per_row (int): Number of seats per row.
        exits (list): List of exit row indices.
        num_simulations (int): Number of Monte Carlo simulations to run.

    Returns:
        evacuation_times (list): List of total evacuation times from all simulations.
    """
    evacuation_times = []
    for _ in range(num_simulations):
        plane = Plane(rows, seats_per_row, exits)
        evacuation_times.append(plane.simulate_evacuation())
    return evacuation_times


# Run the simulation
def main():
    rows = 30           # Number of rows in the plane
    seats_per_row = 6   # Seats per row (standard economy configuration)
    exits = [0, 29]     # Locations of exits (e.g., front and back exits)
    num_simulations = 1000

    evacuation_times = monte_carlo_simulation(rows, seats_per_row, exits, num_simulations)

    # Analyze the results
    average_time = np.mean(evacuation_times)
    std_deviation = np.std(evacuation_times)

    print(f"Average evacuation time: {average_time:.2f} seconds")
    print(f"Standard deviation: {std_deviation:.2f} seconds")

    # Plot the results
    import matplotlib.pyplot as plt
    plt.hist(evacuation_times, bins=30, color='blue', alpha=0.7, edgecolor='black')
    plt.title('Distribution of Evacuation Times')
    plt.xlabel('Evacuation Time (seconds)')
    plt.ylabel('Frequency')
    plt.show()


if __name__ == "__main__":
    main()
