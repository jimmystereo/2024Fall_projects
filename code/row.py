from seat import Seat
from typing import List

class Row:
    """Represents a row of seats on the plane.

    Attributes:
        seats (list): List of Seat objects in this row
        emergency_level (float): Emergency level affecting the row's evacuation

    :param seats_per_row: Number of seats in this row
    :param row_idx: Index of this row
    :param row_speed_factor: Speed adjustment factor for passengers in this row
    :param exits: List of indices of available exits
    :param emergency_level: Emergency level affecting this row's evacuation

    >>> r = Row(seats_per_row=6, row_idx=5, row_speed_factor=1.0, exits=[0, 15, 29], emergency_level=1.0)
    >>> len(r.seats) == 6
    True
    >>> all(isinstance(seat, Seat) for seat in r.seats)
    True
    """
    def __init__(self, seats_per_row: int, row_idx: int, row_speed_factor: float, exits: List[int],
                 emergency_level: float) -> None:
        """Initializes a Row object with a specified number of seats."""
        self.seats = [Seat(row_idx, row_speed_factor, self.assign_exit(row_idx, exits)) for _ in range(seats_per_row)]
        self.emergency_level = emergency_level

    def assign_exit(self, row_idx: int, exits: List[int]) -> int:
        """Assign the nearest exit to the row.

        :param row_idx: ndex of the current row
        :param exits: List of available exit indices

        :return: Index of the nearest exit to this row

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
        """Retrieve evacuation times for passengers in this row.

        :return: Evacuation times for passengers in the row

        >>> r = Row(seats_per_row=6, row_idx=5, row_speed_factor=1.0, exits=[0, 15, 29], emergency_level=1.0)
        >>> all(isinstance(time, float) for time in r.evacuation_times())
        True
        """
        return [seat.passenger.evacuation_time for seat in self.seats if seat.passenger is not None]