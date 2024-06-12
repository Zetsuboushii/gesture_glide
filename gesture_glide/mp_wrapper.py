# Autoren: Nick Büttner,Miguel Themann,Luke Grasser
import time
from typing import List, Any, Callable

import cv2
import mediapipe as mp
import numpy as np
from mediapipe.python import solution_base

from gesture_glide.camera_handler import CameraHandler
from gesture_glide.utils import Observer, Observable, FrameData

HAND_DATA_BUFFER_LENGTH = 20  # Frames


class MPWrapper(Observer, Observable):
    """Wrapper for MediaPipe hand tracking solution. It is responsible for processing frames and notifying observers with mediapipe's results (which contain the hand landmarks)."""
    def __init__(self, camera_handler: CameraHandler):
        super().__init__()
        camera_handler.add_observer(self)
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands()
        self.hand_data_buffer: List[FrameData] = []
        self.last_frame_time = None

    def update(self, observable, *args, **kwargs):
        now = time.time()
        if self.last_frame_time is not None:
            time_from_last_frame = now - self.last_frame_time
            frame_rate = 1 / time_from_last_frame if time_from_last_frame > 0 else None
        else:
            frame_rate = None
        self.last_frame_time = now
        frame = kwargs["frame"]
        frame = cv2.flip(frame, 1)

        # Let mediapipe recognize hands
        results = self.hands.process(frame)
        self.hand_data_buffer.append(FrameData(time.time(), results))
        if len(self.hand_data_buffer) == 1:
            # Initialize first frame so that inter-frame calculations are valid
            # 0.001 needs to be added, as the two time.time() calls can return the same float
            self.hand_data_buffer.append(FrameData(time.time() + 0.001, results))
        if len(self.hand_data_buffer) > HAND_DATA_BUFFER_LENGTH:
            self.hand_data_buffer.pop(0)
        self.notify_observers(metadata=kwargs["metadata"], results=results, frame=frame,
                              frame_rate=frame_rate,
                              hand_data_buffer=self.hand_data_buffer)
