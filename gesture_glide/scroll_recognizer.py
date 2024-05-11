import enum
import math

import cv2
import mediapipe as mp

from gesture_glide.camera_handler import FrameMetadata
from gesture_glide.mp_wrapper import MPWrapper
from gesture_glide.utils import Observer, Observable


class ScrollDirection(enum.Enum):
    UP = 1
    DOWN = -1


class ScrollData:
    direction: ScrollDirection
    distance: float
    # seconds
    duration: float

    def __init__(self, direction: ScrollDirection, distance: float, duration: float = None):
        self.direction = direction
        self.distance = distance
        self.duration = duration if duration is not None else 1.

    def __str__(self):
        return f"<ScrollData(direction={self.direction}, distance={self.distance}, duration={self.duration})>"


class ScrollRecognizer(Observer, Observable):
    def __init__(self, mp_wrapper: MPWrapper):
        super().__init__()
        self.mp_wrapper = mp_wrapper
        self.mp_wrapper.add_observer(self)
        self.previous_y_center_right = None

    def get_euclidean_distance(self, a, b):
        return math.sqrt((a.x - b.x) ** 2 + (a.y - b.y) ** 2)

    def recognize_y_movement(self, previous_y, current_y, height) -> ScrollData | None:
        # Recognizes significant vertical hand movement for scrolling action
        movement_distance = abs(current_y - previous_y)
        movement_threshold = 0.10 * height  # 10% of the frame height
        if movement_distance > movement_threshold:
            if current_y < previous_y:
                return ScrollData(ScrollDirection.UP, movement_distance)
            else:
                return ScrollData(ScrollDirection.DOWN, movement_distance)

    def update(self, observable, *args, **kwargs):
        metadata: FrameMetadata = kwargs["metadata"]
        results = kwargs["results"]
        frame = kwargs["frame"]
        command: ScrollData | None = None
        if results.multi_hand_landmarks:
            for hand_landmarks, handedness in zip(results.multi_hand_landmarks,
                                                  results.multi_handedness):
                if handedness.classification[0].label == 'Right':
                    wrist_y = hand_landmarks.landmark[self.mp_wrapper.mp_hands.HandLandmark.WRIST].y
                    frame_height = metadata.height

                    if self.previous_y_center_right is not None:
                        # TODO: Should only the last command be used if multiple scroll gestures are recognized in one "frame"?
                        command = self.recognize_y_movement(self.previous_y_center_right,
                                                            wrist_y * frame_height, frame_height)

                    self.previous_y_center_right = wrist_y * frame_height

                    mp.solutions.drawing_utils.draw_landmarks(frame, hand_landmarks,
                                                              self.mp_wrapper.mp_hands.HAND_CONNECTIONS)
        if command is not None:
            if command.distance > 250:  # Ensure movement is significant
                print(f"Sending scoll command: {command}")
                self.notify_observers(scroll_command=command, scroll_overlay=frame)
        else:
            cv2.imshow("frame", frame)
            self.notify_observers(scroll_command=command, scroll_overlay=frame)
