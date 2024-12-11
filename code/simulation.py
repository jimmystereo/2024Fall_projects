import numpy as np
import matplotlib.pyplot as plt
from plane import Plane
from typing import List
from concurrent.futures import ProcessPoolExecutor


def simulate_single_plane(args):
    """Wrapper function to create a Plane instance and run the simulation.

    :param args: A tuple containing simulation parameters:
                rows, seats_per_row, seats_per_row_front, front_rows, exits,
                speed_factor, proportion_old, old_in_first_3_rows_prob,
                emergency_level, occupancy_rate

    :return: The evacuation time for a single simulation
    """
    (rows, seats_per_row, seats_per_row_front, front_rows, exits, speed_factor,
     proportion_old, old_in_first_3_rows_prob, emergency_level, occupancy_rate) = args

    plane = Plane(rows=rows,
                  seats_per_row=seats_per_row,
                  seats_per_row_front=seats_per_row_front,
                  front_rows=front_rows,
                  exits=exits,
                  speed_factor=speed_factor,
                  proportion_old=proportion_old,
                  old_in_first_3_rows_prob=old_in_first_3_rows_prob,
                  emergency_level=emergency_level,
                  occupancy_rate=occupancy_rate)
    return plane.simulate_evacuation()

def monte_carlo_simulation(
        rows: int = 30,
        seats_per_row: int = 6,
        seats_per_row_front: int = 4,
        front_rows: int = 4,
        exits: List[int] = [0, 15, 29],
        speed_factor: float = 0.8,
        num_simulations: int = 1000,
        proportion_old: float = 0.3,
        old_in_first_3_rows_prob: float = 0.7,
        emergency_level: float = 1.0,
        occupancy_rate: float = 1.0
) -> List[float]:
    """Runs the Monte Carlo simulation for plane evacuation.

    :param rows: Number of rows in the plane
    :param seats_per_row: Number of seats per row in economy
    :param seats_per_row_front: Number of seats per row in front section
    :param front_rows: Number of rows in front section
    :param exits: List of exit row indices
    :param speed_factor: Speed adjustment factor for front rows
    :param num_simulations: Number of simulations to run
    :param proportion_old: Proportion of elderly passengers
    :param old_in_first_3_rows_prob: Probability of elderly passengers sitting in first three rows
    :param emergency_level: Emergency level affecting urgency and behavior
    :param occupancy_rate: Proportion of occupied seats

    :return: A list of evacuation times from all simulations
    """
    # Create a list of arguments for each simulation
    simulation_args = [(
        rows, seats_per_row, seats_per_row_front, front_rows, exits,
        speed_factor, proportion_old, old_in_first_3_rows_prob,
        emergency_level, occupancy_rate
    )] * int(num_simulations)

    # Use ProcessPoolExecutor to parallelize simulations
    with ProcessPoolExecutor() as executor:
        evacuation_times = list(executor.map(simulate_single_plane, simulation_args))

    return evacuation_times

def plot_results(evacuation_times: List[float], params: dict = None):
    """Plot the results of the Monte Carlo simulation with optional parameter display.

    :param evacuation_times: List of evacuation times from simulations
    :param params: Dictionary of simulation parameters to display
    """
    fig, ax = plt.subplots(figsize=(12, 6))

    # Calculate statistics
    average_time = np.mean(evacuation_times)
    std_deviation = np.std(evacuation_times)

    # Create histogram
    plt.hist(evacuation_times, bins=30, color='orange', alpha=0.7, edgecolor='black')

    # Add vertical line for mean
    plt.axvline(average_time, color='red', linestyle='dashed', linewidth=2)

    # Add titles and labels
    plt.title('Distribution of Evacuation Times')
    plt.xlabel('Evacuation Time (seconds)')
    plt.ylabel('Frequency')

    # Add statistics text
    stats_text = f'Mean: {average_time:.2f}s\nStd Dev: {std_deviation:.2f}s'
    plt.text(0.95, 0.95, stats_text,
             transform=ax.transAxes,
             verticalalignment='top',
             horizontalalignment='right',
             bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

    # Add parameters if provided
    if params:
        params_text = '\n'.join([f'{k}: {v}' for k, v in params.items()])
        plt.text(0.02, 0.95, params_text,
                 transform=ax.transAxes,
                 verticalalignment='top',
                 bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

    plt.tight_layout()

def main():
    # A320 Configuration
    rows = 26
    seats_per_row_front = 2
    seats_per_row = 3
    front_rows = 3
    exits = [0, 9, 10, 25]

    # Simulation parameters
    speed_factor = 0.8
    proportion_old = 0.3
    old_in_first_3_rows_prob = 0.7
    emergency_level = 0.5
    occupancy_rate = 0.8
    num_simulations = 1000

    # Run simulations
    evacuation_times = monte_carlo_simulation(
        rows=rows,
        seats_per_row=seats_per_row,
        seats_per_row_front=seats_per_row_front,
        front_rows=front_rows,
        exits=exits,
        speed_factor=speed_factor,
        num_simulations=num_simulations,
        proportion_old=proportion_old,
        old_in_first_3_rows_prob=old_in_first_3_rows_prob,
        emergency_level=emergency_level,
        occupancy_rate=occupancy_rate
    )

    # Create parameters dictionary for plotting
    params = {
        'Rows': rows,
        'Front Rows': front_rows,
        'Front Row Seats': seats_per_row_front,
        'Economy Seats': seats_per_row,
        'Speed Factor': speed_factor,
        'Emergency Level': emergency_level,
        'Occupancy Rate': f'{occupancy_rate*100}%',
        'Elderly %': f'{proportion_old*100}%',
        'Elderly in Front %': f'{old_in_first_3_rows_prob*100}%'
    }

    # Plot results
    plot_results(evacuation_times, params)
    plt.show()

if __name__ == "__main__":
    main()