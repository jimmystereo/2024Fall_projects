import random
from numba import njit

@njit
def calculate_evacuation_time(panic_level: float, move_time: float, row_speed_factor: float,
                              distance_to_exit: int, baggage_delay: float) -> float:
    """Calculate the evacuation time considering the distance to exit and the row's speed factor.

    :param panic_level: The passenger's panic level (0 to 1, where 1 is maximum panic)
    :param move_time: Time taken to move per unit distance, based on passenger mobility (in seconds)
    :param row_speed_factor: Speed adjustment factor for the passenger's row (1.0 is normal speed)
    :param distance_to_exit: Distance between the passenger's row and the assigned exit (in row units)
    :param baggage_delay: Delay caused by carrying baggage (in seconds)

    :return: Total evacuation time in seconds

    >>> calculate_evacuation_time(0.5, 4.0, 1.0, 10, 1.0)
    21.0
    >>> calculate_evacuation_time(0.0, 1.0, 1.0, 0, 0.0)
    0.0
    >>> calculate_evacuation_time(1.0, 10.0, 2.0, 50, 5.0)
    1005.0
    >>> calculate_evacuation_time(0.5, 4.0, 1.0, 5, 1.0) < calculate_evacuation_time(0.5, 4.0, 1.0, 10, 1.0)
    True
    >>> calculate_evacuation_time(0.5, 4.0, 1.0, 10, 1.0) < calculate_evacuation_time(1.0, 4.0, 1.0, 10, 1.0)
    True
    """
    return baggage_delay + (panic_level * move_time * row_speed_factor * distance_to_exit)


class Passenger:
    """Represents a passenger in an aircraft evacuation simulation.

    Attributes:
        panic_level (float): Passenger's panic level (0 to 1, where 1 is maximum panic)
        baggage_delay (float): Delay caused by carrying baggage in seconds (0 to 1)
        age (str): Age category, either 'young' or 'old'
        move_time (float): Time taken to move per unit distance (1-4 seconds for young, 8-10 for old)
        row_speed_factor (float): Speed adjustment factor for the passenger's row (1.0 is normal speed)
        exit_idx (int): Index of the assigned exit
        distance_to_exit (int): Distance to the assigned exit in row units
        evacuation_time (float): Total calculated evacuation time in seconds
        row_idx (int): Index of the passenger's seat row
        order (int): Order number of the passenger in the evacuation sequence
        final_time (float): Final evacuation time after considering all delays and congestion

    :param row_idx: Index of the passenger's seat row (0-based)
    :param row_speed_factor: Speed adjustment based on row location (1.0 is normal speed)
    :param exit_idx: Index of the assigned exit
    :param age: Age category ('young' or 'old', defaults to "young")
    :param emergency_level: Emergency level affecting passenger behavior (0 to 1, where 1 is most severe). Defaults to 1.0

    >>> p = Passenger(row_idx=5, row_speed_factor=0.8, exit_idx=10, age="young", emergency_level=1.0)
    >>> isinstance(p, Passenger)
    True
    >>> p.evacuation_time > 0 # Evacuation time is always positive
    True

    >>> # Test evacuation time differences between young and old
    >>> py = Passenger(row_idx=5, row_speed_factor=1.0, exit_idx=10, age="young")
    >>> po = Passenger(row_idx=5, row_speed_factor=1.0, exit_idx=10, age="old")
    >>> po.move_time > py.move_time # Old passengers should take longer to move
    True
    """
    def __init__(self, row_idx: int, row_speed_factor: float, exit_idx: int, age: str = "young", emergency_level: float = 1.0) -> None:
        """Initializes a Passenger object with evacuation-related characteristics.

        Assigns random values for panic level, and baggage delay.
        Adjusts mobility based on age category and applies emergency level effects.
        Calculates initial evacuation time based on all factors.
        """
        self.panic_level = random.uniform(0, 1)
        self.baggage_delay = random.uniform(0, 1)
        self.age = age
        self.row_idx = row_idx
        self.order = None
        # Adjust physical mobility based on age
        if self.age == 'old':
            self.move_time = random.uniform(8, 10)  # Older passengers are less mobile
        else:
            self.move_time = random.uniform(1, 4)  # Younger passengers are more mobile

        self.row_speed_factor = row_speed_factor  # Speed factor for the row
        self.exit_idx = exit_idx  # Assigned exit index
        self.distance_to_exit = abs(row_idx - exit_idx)  # Distance to the nearest exit

        # Apply emergency level adjustments
        self.apply_emergency_level(emergency_level)
        self.final_time = None
        # Calculate evacuation time
        self.evacuation_time = calculate_evacuation_time(
            self.panic_level, self.move_time, self.row_speed_factor, self.distance_to_exit, self.baggage_delay
        )

    def apply_emergency_level(self, emergency_level: float) -> None:
        """Adjust panic level, baggage delay, and physical mobility based on the emergency level.

        Higher emergency levels increase panic but reduce baggage delays as passengers
        prioritize evacuation over belongings. Physical mobility increases with emergency
        level as adrenaline and urgency affect passenger movement.

        :param emergency_level: Emergency level affecting passenger behavior (0 to 1, where 1 is most severe)

        >>> p = Passenger(row_idx=5, row_speed_factor=0.8, exit_idx=10, emergency_level=0.5)
        >>> init_panic = p.panic_level
        >>> init_move_time = p.move_time
        >>> p.apply_emergency_level(0.5)
        >>> 0 <= p.panic_level <= 1
        True
        >>> 0 <= p.move_time < init_move_time
        True
        """
        self.panic_level *= emergency_level  # Panic level increases with emergency level
        self.panic_level = min(self.panic_level, 1)  # Cap at 1 for maximum panic level

        self.baggage_delay *= (1 - emergency_level * 0.5)  # Baggage delay decreases with higher emergency level

        # Physical mobility could increase as people are more urgent during high emergency levels
        self.move_time *= (1 - emergency_level * 0.2)  # Increase mobility as emergency level rises