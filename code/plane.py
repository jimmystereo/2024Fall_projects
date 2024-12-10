import random
from row import Row
from passenger import Passenger
from typing import List, Tuple
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

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
    def __init__(self, rows: int, seats_per_row: int, exits: List[int], speed_factor: float = 0.8,
                 door_opening_time: float = 2,proportion_old: float = 0.3, old_in_first_3_rows_prob: float = 0.7,
                 emergency_level: float = 1.0,occupancy_rate: float = 1.0) -> None:
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
        self.exits_lines = None
        # Adjust seats per row for the first three rows
        for idx in range(rows):
            current_seats_per_row = 2 if idx < 3 else seats_per_row
            self.rows.append(Row(current_seats_per_row, idx, speed_factor if idx < 3 else 1, exits, emergency_level))

        self.line = self.generate_line(emergency_level)

    def generate_line(self, emergency_level: float) -> List[Tuple[int, int, float]]:
        """Generates a list of passengers with their assigned nearest exit and age.
        Includes a higher probability for old passengers to sit in the first 3 rows.
        Only a proportion of seats are occupied based on the occupancy rate.

        :param emergency_level: Emergency level

        :return: List of tuples representing passenger data
        """
        line = []
        order = 0
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

                # Create a Passenger instance
                passenger = Passenger(row_idx, seat.row_speed_factor, seat.exit_idx, age, emergency_level)
                evac_time = passenger.evacuation_time
                nearest_exit = passenger.exit_idx

                # Assign the passenger to the seat
                seat.passenger = passenger
                order += 1
                seat.passenger.order = order
                # Add passenger information to the line
                line.append((row_idx, nearest_exit, evac_time, passenger))
        return line

    def evacuation_times(self) -> List[float]:
        """Retrieve adjusted evacuation times for all passengers in the plane,
        considering delays caused by slower passengers in front of them across rows.

        :return: List of adjusted evacuation times for passengers in the entire plane
        """
        times = []
        for row in self.rows:
            for seat in row.seats:
                if seat.passenger is not None:
                    if times:
                        # Adjust based on the maximum time of passengers ahead (within the row and across rows)
                        times.append(max(times[-1], seat.passenger.evacuation_time))
                    else:
                        times.append(seat.passenger.evacuation_time)
        return times

    def simulate_evacuation(self) -> float:
        """Simulate the evacuation process with dynamic exits, considering separate queues for each exit and congestion, and ordering by distance to the exit."""

        # Initialize the dictionary for exits with dynamic allocation (using exit indexes)
        exits = {i: [] for i in self.exits}  # where self.exits can represent a list or range of exit indexes

        # Dynamically assign passengers to exits based on their exit index
        for p in self.line:
            nearest_exit = p[1]
            exits[nearest_exit].append(p[3])
        self.exits_lines = exits
    # Helper function to simulate evacuation for each exit, sorted by distance_to_exit
        def evacuate_from_exit(passengers):
            # Sort the passengers by their distance to the exit (ascending)
            # passengers_sorted_by_distance = sorted(passengers, key=lambda p: p.distance_to_exit)

            evacuation_times = []

            # For each passenger at this exit, calculate their final evacuation time
            for idx, passenger in enumerate(passengers):
                if idx == 0:
                    # First passenger evacuates without delay
                    passenger.final_time = passenger.evacuation_time
                    evacuation_times.append(passenger.final_time)
                else:
                    # Each subsequent passenger is delayed by the maximum time of the previous passengers
                    max_time_ahead = max([evacuation_times[i] for i in range(idx)])
                    passenger.final_time = max(max_time_ahead, passenger.evacuation_time)
                    evacuation_times.append(passenger.final_time)

            # Return the latest evacuation time for this exit
            return max(evacuation_times)

        # Simulate evacuation for all exits and calculate the time per exit
        evacuation_times_for_exits = []
        for exit_idx in exits:
            evacuation_times_for_exits.append(evacuate_from_exit(exits[exit_idx]))

        # The total evacuation time is the maximum time across all exits
        total_evacuate_time = max(evacuation_times_for_exits)

        return total_evacuate_time


    def draw_seatmap(self, color_mode):
        """
        Draws the seatmap of the plane, showing passenger age, speed factor, evacuation time,
        and nearest exit with a gradient color based on evacuation time.
        Passengers with smaller 'order' values will be placed closer to their nearest exit.
        """
        fig, ax = plt.subplots(figsize=(12, len(self.rows) * 0.5))  # Dynamic height based on rows

        # Create a colormap for evacuation time (green to red)
        cmap = plt.cm.RdYlGn_r  # Reverse colormap to go from green (low) to red (high)

        # Calculate min and max evacuation time for dynamic normalization
        evac_times = [seat.passenger.evacuation_time for row in self.rows for seat in row.seats if seat.passenger]
        min_evacuate_time = min(evac_times) if evac_times else 0
        max_evacuate_time = max(evac_times) if evac_times else 10
        norm = mcolors.Normalize(vmin=min_evacuate_time, vmax=max_evacuate_time)

        # Collect all passengers sorted by order and their nearest exit
        all_passengers = []
        for row_idx, row in enumerate(self.rows):
            for seat_idx, seat in enumerate(row.seats):
                if seat.passenger:
                    nearest_exit = min(self.exits, key=lambda exit_idx: abs(exit_idx - row_idx))
                    all_passengers.append((seat.passenger.order, nearest_exit, row_idx, seat_idx, seat.passenger))

        # Sort passengers by their order and nearest exit
        all_passengers.sort(key=lambda x: (x[1], x[0]))  # Sort by exit, then by order

        # Create a modified seat grid to rearrange passengers
        modified_seat_grid = [[None for _ in range(len(row.seats))] for row in self.rows]

        # Place passengers in the grid
        placed_passengers = set()
        for order, nearest_exit, orig_row, orig_seat, passenger in all_passengers:
            # Find appropriate rows near the exit
            exit_rows = [row_idx for row_idx in range(len(self.rows))
                         if min(self.exits, key=lambda x: abs(x - row_idx)) == nearest_exit]
            exit_rows.sort(key=lambda row_idx: abs(row_idx - nearest_exit))

            # Find an unoccupied seat in the appropriate rows
            placed = False
            for target_row_idx in exit_rows:
                for seat_idx in range(len(self.rows[target_row_idx].seats)):
                    if modified_seat_grid[target_row_idx][seat_idx] is None:
                        modified_seat_grid[target_row_idx][seat_idx] = passenger
                        placed = True
                        placed_passengers.add(passenger)
                        break
                if placed:
                    break

        # Loop through rows and seats to plot the seatmap
        for row_idx, row in enumerate(self.rows):
            for seat_idx, seat in enumerate(row.seats):
                x, y = seat_idx, len(self.rows) - row_idx - 1  # Invert y-axis for top-left orientation

                # Use the modified seat grid for passenger placement
                passenger = modified_seat_grid[row_idx][seat_idx] if modified_seat_grid[row_idx][seat_idx] is not None else seat.passenger

                if passenger:
                    if color_mode == 'final':
                        evac_time = passenger.final_time
                    elif color_mode == 'initial':
                        evac_time = passenger.evacuation_time

                    facecolor = cmap(norm(evac_time))  # Map evacuation time to color

                    # Dynamically assign exit based on proximity (distance from seat to exits)
                    nearest_exit = min(self.exits, key=lambda exit_idx: abs(exit_idx - row_idx))
                    exit_label = str(nearest_exit)  # Label with exit position
                else:
                    facecolor = 'white'  # Empty seat
                    exit_label = ""  # No exit label for empty seats

                # Draw seat as a rectangle
                ax.add_patch(plt.Rectangle((x, y), 1, 1, edgecolor='black', facecolor=facecolor))

                # Add text with evacuation time and age inside the rectangle
                if passenger:
                    age = passenger.age
                    evac_time_text = f"{passenger.evacuation_time:.2f}"
                    final_time_text = f"{passenger.final_time:.2f}"
                    order = passenger.order
                else:
                    age = "Empty"
                    evac_time_text = "-"
                    final_time_text = "-"
                    order = -1

                ax.text(
                    x + 0.5,
                    y + 0.5,
                    f"{age}\n{evac_time_text}\n{final_time_text}\n{str(order)} {exit_label}",
                    ha='center',
                    va='center',
                    fontsize=8
                )

            # Highlight exits
            for exit_idx in self.exits:
                x, y = -1, len(self.rows) - exit_idx - 1  # Exit position at the left of each row
                ax.add_patch(plt.Rectangle((x, y), 1, 1, edgecolor='black', facecolor='green'))
                ax.text(x + 0.5, y + 0.5, "EXIT", ha='center', va='center', fontsize=8, color='white')

        # Draw plane frame
        max_seats_per_row = max(len(row.seats) for row in self.rows)
        ax.add_patch(plt.Rectangle(
            (-1, -1), max_seats_per_row + 2, len(self.rows) + 1, edgecolor='black', facecolor='none', linewidth=2
        ))

        # Set axis limits and labels
        ax.set_xlim(-2, max(len(row.seats) for row in self.rows) + 1)
        ax.set_ylim(-1, len(self.rows))
        ax.set_aspect('equal')
        ax.axis('off')

        # Add colorbar for evacuation time
        sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
        sm.set_array([])  # No data for ScalarMappable
        cbar = plt.colorbar(sm, ax=ax, orientation='vertical', fraction=0.02, pad=0.04)
        cbar.set_label('Evacuation Time (seconds)')

        # Title and show
        plt.title("Plane Seatmap with Gradient Evacuation Time and Assigned Exits")
        plt.tight_layout()
        plt.show()# Assuming Plane, Row, and Passenger classes are defined as in your earlier setup
# To use:
rows = 30           # Number of rows in the plane
seats_per_row = 3   # Seats per row (standard economy configuration)
exits = [0, 15, 29] # Locations of exits (front, middle, back exits)
speed_factor = 0.6  # First three rows move faster (80% of the normal time)
door_opening_time = 2  # Time for middle exit door to open (2 seconds)
num_simulations = 1000
proportion_old = 0.3  # 30% old passengers
old_in_first_3_rows_prob = 0.6  # 70% chance for old passengers to sit in the first 3 rows
emergency_level = 0.9  # Emergency level: 0.0 (low) to 1.0 (high)
occupancy_rate = 1  # 80% of seats are occupied

plane = Plane(rows, seats_per_row, exits, speed_factor, door_opening_time, proportion_old,
              old_in_first_3_rows_prob, emergency_level, occupancy_rate)
plane.simulate_evacuation()
# plane.rows[3].seats[1].passenger.age
plane.draw_seatmap('initial')
plane.draw_seatmap('final')

for i in plane.exits_lines[0]:
    print(i)