import enum
import time
from typing import List, Tuple, Any

import cv2

from gesture_glide.camera_handler import CameraHandler
from gesture_glide.utils import Observer, Observable
import mediapipe as mp

HAND_DATA_BUFFER = 20  # Frames


class HandMovementState(enum.Enum):
    NO_MOVEMENT = 0
    MOVEMENT_BEGIN = 1
    MOVEMENT_END = 2
    IN_MOVEMENT = 3

class FrameData:
    time: float
    results: Any
    hand_movement_state: HandMovementState | None
    def __init__(self, time: float, results: Any, hand_movement_state: HandMovementState = None):
        self.time = time
        self.results = results
        self.hand_movement_state = hand_movement_state

class MPWrapper(Observer, Observable):
    def __init__(self, camera_handler: CameraHandler):
        super().__init__()
        camera_handler.add_observer(self)
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands()
        self.hand_data_buffer: List[FrameData] = []

    def update(self, observable, *args, **kwargs):
        frame = kwargs["frame"]
        frame = cv2.cvtColor(cv2.flip(frame, 1), cv2.COLOR_BGR2RGB)
        results = self.hands.process(frame)
        self.hand_data_buffer.append(FrameData(time.time(), results))
        if len(self.hand_data_buffer) > HAND_DATA_BUFFER - 1:
            self.hand_data_buffer.pop(0)
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)  # TODO: Remove if appropriate
        # Multihand landmarks -> hand landmarks -> landmark[x, y, z]
        # TODO: add frame rate from camera handler for hmr
        self.notify_observers(metadata=kwargs["metadata"], frame=frame,
                              hand_data_buffer=self.hand_data_buffer)
