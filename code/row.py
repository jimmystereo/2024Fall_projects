from seat import Seat
from typing import List

class Row:
    """Represents a row of seats on the plane.

    Attributes:
        seats (list): List of Seat objects in this row
        emergency_level (float): Emergency level affecting the row's evacuation time (0 to 1)
        row_idx (int): Index of this row in the plane
        row_speed_factor (float): Speed multiplier affecting passenger movement in this row
        exits (List[int]): List of available exit indices for this row

    :param seats_per_row: Number of seats in this row
    :param row_idx: Index of this row in the plane (0-based)
    :param row_speed_factor: Speed adjustment factor for passengers in this row (1.0 is normal speed)
    :param exits: List of indices of available exits in the plane
    :param emergency_level: Emergency level affecting this row's evacuation (0 to 1, where 1 is most severe)

    >>> r = Row(seats_per_row=6, row_idx=5, row_speed_factor=1.0, exits=[0, 15, 29], emergency_level=1.0)
    >>> len(r.seats) == 6
    True
    >>> all(isinstance(seat, Seat) for seat in r.seats)
    True
    """
    def __init__(self, seats_per_row: int, row_idx: int, row_speed_factor: float, exits: List[int],
                 emergency_level: float) -> None:
        """Initializes a Row object with a specified number of seats.

        Creates seats with the given row parameters and assigns the nearest exit to each seat.
        The assigned exit will influence passenger evacuation paths and times.
        """
        self.seats = [Seat(row_idx, row_speed_factor, self.assign_exit(row_idx, exits)) for _ in range(seats_per_row)]
        self.emergency_level = emergency_level

    def assign_exit(self, row_idx: int, exits: List[int]) -> int:
        """Assign the nearest exit to the row based on minimum distance.

        :param row_idx: Index of the current row (0-based)
        :param exits: List of available exit indices in ascending order

        :return: Index of the nearest exit to this row based on absolute distance

        >>> row = Row(seats_per_row=6, row_idx=5, row_speed_factor=1.0, exits=[0, 15, 29], emergency_level=1.0)
        >>> row.assign_exit(5, [0, 15, 29]) in [0, 15, 29]
        True
        >>> row.assign_exit(13, [0, 15, 29]) == 15
        True
        >>> row.assign_exit(0, [0, 15, 29]) == 0
        True
        >>> row.assign_exit(29, [0, 15, 29]) == 29
        True
        """
        # Assign the nearest exit to the row
        return min(exits, key=lambda exit_idx: abs(exit_idx - row_idx))

    def evacuation_times(self) -> List[float]:
        """Retrieve adjusted evacuation times for passengers in this row,
        accounting for delays caused by slower passengers in front.

        The evacuation time for each passenger is adjusted based on the maximum
        evacuation time of all passengers ahead of them in the same row, ensuring
        realistic evacuation flow where passengers can't overtake those in front.

        :return: List of adjusted evacuation times for passengers in the row,
                where each time accounts for delays from preceding passengers
        """
        times = []
        for seat in self.seats:
            if seat.passenger is not None:
                if times:
                    # Adjust based on the maximum time of passengers ahead
                    times.append(max(times[-1], seat.passenger.evacuation_time))
                else:
                    times.append(seat.passenger.evacuation_time)
        return times