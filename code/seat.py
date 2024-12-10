from passenger import Passenger


class Seat:
    """Represents a seat on the plane, which may be occupied by a passenger.

    Attributes:
        passenger (Passenger): Optional. Passenger occupying the seat

    :param row_idx: Index of the row containing this seat
    :param row_speed_factor: Speed factor for the seat's row
    :param exit_idx: Index of the nearest exit

    >>> seat = Seat(row_idx=5, row_speed_factor=1.0, exit_idx=10)
    >>> isinstance(seat, Seat)
    True
    """
    def __init__(self, row_idx: int, row_speed_factor: float, exit_idx: int) -> None:
        """Initializes a Seat object with its location and evacuation parameters."""
        self.passenger = None
        self.row_idx = row_idx
        self.row_speed_factor = row_speed_factor
        self.exit_idx = exit_idx