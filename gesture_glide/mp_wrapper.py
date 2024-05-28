import enum
import time
from typing import List, Tuple, Any, Callable
import cv2
import mediapipe as mp
from gesture_glide.camera_handler import CameraHandler
from gesture_glide.utils import Observer, Observable

HAND_DATA_BUFFER = 20  # Frames


class HandMovementState(enum.Enum):
    NO_MOVEMENT = 0
    MOVEMENT_BEGIN = 1
    MOVEMENT_END = 2
    IN_MOVEMENT = 3


class HandMovementType(enum.Enum):
    NONE = 0
    SCROLLING = 1
    ZOOMING = 2


class FrameData:
    time: float
    results: Any
    hand_movement_state: HandMovementState
    hand_movement_type: HandMovementType

    def __init__(self, time: float, results: Any, hand_movement_state: HandMovementState = None,
                 hand_movement_type: HandMovementType = None):
        self.time = time
        self.results = results
        self.hand_movement_state = hand_movement_state
        self.hand_movement_type = hand_movement_type


class MPWrapper(Observer, Observable):
    def __init__(self, camera_handler: CameraHandler):
        super().__init__()
        camera_handler.add_observer(self)
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands()
        self.hand_data_buffer: List[FrameData] = []
        self.capture_callback: Callable[[List], None] = None
        self.recognition_callback: Callable[[List], None] = None

    def update(self, observable, *args, **kwargs):
        frame = kwargs["frame"]
        frame = cv2.cvtColor(cv2.flip(frame, 1), cv2.COLOR_BGR2RGB)
        results = self.hands.process(frame)
        self.hand_data_buffer.append(FrameData(time.time(), results))
        if len(self.hand_data_buffer) > HAND_DATA_BUFFER - 1:
            self.hand_data_buffer.pop(0)
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)  # TODO: Remove if appropriate
        self.notify_observers(metadata=kwargs["metadata"], results=results, frame=frame,
                              hand_data_buffer=self.hand_data_buffer)

        if self.capture_callback and cv2.waitKey(1) & 0xFF == ord('s'):
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    landmarks = [(lm.x, lm.y, lm.z) for lm in hand_landmarks.landmark]
                    self.capture_callback(landmarks)

        if self.recognition_callback:
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    landmarks = [(lm.x, lm.y, lm.z) for lm in hand_landmarks.landmark]
                    self.recognition_callback(landmarks)
