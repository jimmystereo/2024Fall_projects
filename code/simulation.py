import numpy as np
import matplotlib.pyplot as plt
from plane import Plane
from typing import List
from concurrent.futures import ProcessPoolExecutor


def simulate_single_plane(args):
    """Wrapper function to create a Plane instance and run the simulation.

    :param args: A tuple containing simulation parameters:
                 rows, seats_per_row, exits, speed_factor, door_opening_time,
                 proportion_old, old_in_first_3_rows_prob, emergency_level, occupancy_rate

    :return: The evacuation time for a single simulation

    >>> args = (10, 6, [0, 5], 0.8, 2, 0.3, 0.7, 1.0, 0.9)
    >>> isinstance(simulate_single_plane(args), float)
    True
    """
    rows, seats_per_row, exits, speed_factor, door_opening_time, proportion_old, \
    old_in_first_3_rows_prob, emergency_level, occupancy_rate = args

    plane = Plane(rows, seats_per_row, exits, speed_factor, door_opening_time, proportion_old,
                  old_in_first_3_rows_prob, emergency_level, occupancy_rate)
    return plane.simulate_evacuation()

def monte_carlo_simulation(rows: int = 30, seats_per_row: int = 6, exits: List[int] = [0, 15, 29],
                           speed_factor: float = 0.8, door_opening_time: float = 2, num_simulations: int = 1000,
                           proportion_old: float = 0.3, old_in_first_3_rows_prob: float = 0.7,
                           emergency_level: float = 1.0, occupancy_rate: float = 1.0) -> List[float]:
    """Runs the Monte Carlo simulation for plane evacuation.

    :param rows: Number of rows in the plane
    :param seats_per_row: Number of seats per row
    :param exits: List of exit row indices
    :param speed_factor: Speed adjustment factor for specific conditions
    :param door_opening_time: Time for exit doors to open
    :param num_simulations: Number of simulations to run
    :param proportion_old: Proportion of elderly passengers
    :param old_in_first_3_rows_prob: Probability of elderly passengers sitting in the first three rows
    :param emergency_level: Emergency level affecting urgency and behavior
    :param occupancy_rate: Proportion of occupied seats

    :return: A list of evacuation times from all simulations

    >>> times = monte_carlo_simulation(rows=10, seats_per_row=6, num_simulations=100, exits=[0, 5])
    >>> len(times) == 100
    True
    >>> all(time > 0 for time in times)
    True
    >>> np.mean(times) > 0
    True
    >>> 0 < np.std(times) < 50
    True
    """
    # Create a list of arguments for each simulation
    simulation_args = [(rows, seats_per_row, exits, speed_factor, door_opening_time,
                        proportion_old, old_in_first_3_rows_prob, emergency_level, occupancy_rate)] * num_simulations

    # Use ProcessPoolExecutor to parallelize simulations
    with ProcessPoolExecutor() as executor:
        evacuation_times = list(executor.map(simulate_single_plane, simulation_args))

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

    evacuation_times = monte_carlo_simulation(rows, seats_per_row, exits, speed_factor, door_opening_time,
                                              num_simulations, proportion_old, old_in_first_3_rows_prob,
                                              emergency_level, occupancy_rate)

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