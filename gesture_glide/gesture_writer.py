import json
import logging
import os

from gesture_glide.mp_wrapper import MPWrapper
from gesture_glide.config import Config
from gesture_glide.utils import Observer, Observable


class GestureWriter(Observer, Observable):
    """Gesture data management (for user configurable gestures)."""
    def __init__(self, config: Config, mp_wrapper: MPWrapper):
        super().__init__()
        self.landmarks = None
        self.config = config
        mp_wrapper.add_observer(self)

    def update(self, observable, *args, **kwargs):
        current_landmarks = kwargs["results"].multi_hand_landmarks
        if current_landmarks is not None:
            self.landmarks = current_landmarks

    def capture_gesture(self, gesture_name: str):
        self.save_gesture(gesture_name, self.landmarks)
        logging.debug(f"Gesture '{gesture_name}' was saved")

        # mp_wrapper.set_capture_callback(capture_callback)

    def save_gesture(self, gesture_name: str, landmarks: list):
        gesture_data = {gesture_name: list(map(lambda landmark: [landmark.x, landmark.y, landmark.z], landmarks[0].landmark))}
        if os.path.exists("gestures.json"):
            with open("gestures.json", "r") as file:
                try:
                    data = json.load(file)
                except json.JSONDecodeError:
                    data = {}
            data.update(gesture_data)
        else:
            data = gesture_data

        with open("gestures.json", "w") as file:
            json.dump(data, file, indent=4)
