import enum
from typing import Any, List
import pyautogui


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


class RecognizedGesture(enum.Enum):
    OPEN_ROULETTE = 0
    ROULETTE_PLUS = 1
    ROULETTE_MINUS = 2


class GestureMode(enum.Enum):
    DEFAULT = 0
    ROULETTE = 1


class ScrollData:
    direction: ScrollDirection
    speed: float

    def __init__(self, direction: ScrollDirection, speed: float = None):
        self.direction = direction
        self.speed = speed

    def __str__(self):
        return f"<ScrollData(direction={self.direction},speed={self.speed})>"


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
    speed: float | None
    direction: Directions | None

    def __init__(self, handedness: Handedness, hand_movement_state: HandMovementState,
                 hand_movement_type: HandMovementType, speed: float | None, direction: Directions | None):
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
    mono_hand_movement_data: HandMovementData | None = None

    def __init__(self, time: float, results: Any, left_hand_movement_data: HandMovementData = None,
                 right_hand_movement_data: HandMovementData = None, mono_hand_movement_data: HandMovementData = None):
        self.time = time
        self.results = results
        self.left_hand_movement_data = left_hand_movement_data
        self.right_hand_movement_data = right_hand_movement_data
        self.mono_hand_movement_data = mono_hand_movement_data

    def has_hand_data(self, handedness: Handedness | None = None):
        if handedness is None:
            return self.left_hand_movement_data is not None or self.right_hand_movement_data is not None
        elif handedness == Handedness.LEFT:
            return self.left_hand_movement_data is not None
        else:
            return self.right_hand_movement_data is not None

    def get_hand_movement_data(self, handedness: Handedness) -> HandMovementData:
        return self.left_hand_movement_data if handedness == Handedness.LEFT else self.right_hand_movement_data


def get_last_valid_frame_data(hand_data_buffer: List[FrameData], counter: int,
                              handedness: Handedness | None) -> FrameData | None:
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


def switch_to_previous_screen():
    pyautogui.hotkey('alt', 'tab')
