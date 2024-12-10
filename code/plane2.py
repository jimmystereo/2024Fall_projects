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
                nearest_exit = min(self.exits, key=lambda exit_idx: abs(exit_idx - row_idx))

                # Assign the passenger to the seat
                seat.passenger = passenger

                # Add passenger information to the line
                line.append((row_idx, nearest_exit, evac_time))
        return line


    def simulate_evacuation(self) -> float:
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

    def draw_seatmap(self):
        """
        Draws the seatmap of the plane, showing passenger age and speed factor with a gradient color
        based on evacuation time.
        """
        fig, ax = plt.subplots(figsize=(12, len(self.rows) * 0.5))  # Dynamic height based on rows

        # Create a colormap for evacuation time (green to red)
        cmap = plt.cm.RdYlGn_r  # Reverse colormap to go from green (low) to red (high)
        norm = mcolors.Normalize(vmin=0, vmax=10)  # Normalize evacuation time between 0 and 10 seconds (adjust range as needed)

        # Loop through rows and seats
        for row_idx, row in enumerate(self.rows):
            for seat_idx, seat in enumerate(row.seats):
                x, y = seat_idx, len(self.rows) - row_idx - 1  # Invert y-axis for top-left orientation

                if seat.passenger:
                    evac_time = seat.passenger.evacuation_time
                    facecolor = cmap(norm(evac_time))  # Map evacuation time to color
                else:
                    facecolor = 'white'  # Empty seat

                # Draw seat as a rectangle
                ax.add_patch(plt.Rectangle((x, y), 1, 1, edgecolor='black', facecolor=facecolor))

                # Add text with evacuation time inside the rectangle
                age = seat.passenger.age if seat.passenger else "Empty"
                evac_time_text = f"{seat.passenger.move_time:.2f}" if seat.passenger else "-"
                ax.text(
                    x + 0.5,
                    y + 0.5,
                    f"{age}\n{evac_time_text}",
                    ha='center',
                    va='center',
                    fontsize=8
                )

        # Highlight exits
        for exit_idx in self.exits:
            x, y = -1, len(self.rows) - exit_idx - 1  # Exit position at the top-left of each row
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
        plt.title("Plane Seatmap with Gradient Evacuation Time")
        plt.tight_layout()
        plt.show()
# Assuming Plane, Row, and Passenger classes are defined as in your earlier setup
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
plane.draw_seatmap()
