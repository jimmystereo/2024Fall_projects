import numpy as np
import matplotlib.pyplot as plt
from plane import Plane


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