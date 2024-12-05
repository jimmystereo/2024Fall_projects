from mcsim3 import *

def main():
    """
    Main function to run the evacuation simulation and visualize results.
    """
    rows = 30           # Number of rows in the plane
    seats_per_row = 6   # Seats per row (standard economy configuration)
    exits = [0, 15]     # Locations of exits (e.g., front and back exits)
    num_simulations = 100

    evacuation_times = monte_carlo_simulation(rows, seats_per_row, exits, num_simulations)

    # Analyze the results
    average_time = np.mean(evacuation_times)
    std_deviation = np.std(evacuation_times)

    print(f"Average evacuation time: {average_time:.2f} seconds")
    print(f"Standard deviation: {std_deviation:.2f} seconds")

    # Plot the results
    plt.hist(evacuation_times, bins=30, color='green', alpha=0.7, edgecolor='black')
    plt.title('Distribution of Evacuation Times')
    plt.xlabel('Evacuation Time (seconds)')
    plt.ylabel('Frequency')
    plt.show()


if __name__ == "__main__":
    main()
