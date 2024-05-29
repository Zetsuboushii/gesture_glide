import enum
from typing import Any, List


class Observable:
    def __init__(self):
        self.observers = []

    def add_observer(self, observer):
        if observer not in self.observers:
            self.observers.append(observer)

    def remove_observer(self, observer):
        if observer in self.observers:
            self.observers.remove(observer)

    def notify_observers(self, *args, **kwargs):
        for observer in self.observers:
            observer.update(self, *args, **kwargs)

class Observer:
    def update(self, observable, *args, **kwargs):
        pass


class Handedness(enum.StrEnum):
    LEFT = "Left"
    RIGHT = "Right"


class ScrollDirection(enum.Enum):
    UP = 1
    DOWN = -1


class Directions(enum.Enum):
    UP = 0
    DOWN = 1
    LEFT = 2
    RIGHT = 3


class ScrollData:
    direction: ScrollDirection
    distance: float
    duration: float

    def __init__(self, direction: ScrollDirection, distance: float, duration: float = None):
        self.direction = direction
        self.distance = distance
        self.duration = duration if duration is not None else 1.

    def __str__(self):
        return f"<ScrollData(direction={self.direction}, distance={self.distance}, duration={self.duration})>"


class ZoomData:
    zoom_in: bool
    scale: float

    def __init__(self, zoom_in: bool, scale: float):
        self.zoom_in = zoom_in
        self.scale = scale

    def __str__(self):
        return f"<ZoomData(zoom_in={self.zoom_in}, scale={self.scale})>"


class HandMovementState(enum.Enum):
    NO_MOVEMENT = 0
    MOVEMENT_BEGIN = 1
    MOVEMENT_END = 2
    IN_MOVEMENT = 3
    QUASI_END = 4


class HandMovementType(enum.Enum):
    NONE = 0
    SCROLLING = 1
    ZOOMING = 2


class HandMovementData:

    handedness: Handedness
    hand_movement_state: HandMovementState
    hand_movement_type: HandMovementType
    speed: float
    direction: Directions

    def __init__(self, handedness: Handedness, hand_movement_state: HandMovementState,
                    hand_movement_type: HandMovementType, speed: float, direction: Directions):
        self.handedness = handedness
        self.hand_movement_state = hand_movement_state
        self.hand_movement_type = hand_movement_type
        self.speed = speed
        self.direction = direction


class FrameData:
    time: float
    results: Any
    left_hand_movement_data: HandMovementData = None
    right_hand_movement_data: HandMovementData = None
    def __init__(self, time: float, results: Any, left_hand_movement_data: HandMovementData = None,
                 right_hand_movement_data: HandMovementData = None):
        self.time = time
        self.results = results
        self.left_hand_movement_data = left_hand_movement_data
        self.right_hand_movement_data = right_hand_movement_data

    def has_hand_data(self, handedness: Handedness | None = None):
        if handedness is None:
            return self.left_hand_movement_data is not None or self.right_hand_movement_data is not None
        elif handedness == Handedness.LEFT:
            return self.left_hand_movement_data is not None
        else:
            return self.right_hand_movement_data is not None


def get_last_valid_frame_data(hand_data_buffer: List[FrameData], counter: int, handedness: Handedness | None) -> FrameData | None:
    if len(hand_data_buffer) == 0:
        return None
    i = -1
    count = 1
    frame_data = hand_data_buffer[i]
    try:
        while frame_data.has_hand_data(handedness):
            if count == counter:
                return frame_data
            i -= 1
            count += 1
            frame_data = hand_data_buffer[i]
    except IndexError:
        return None


