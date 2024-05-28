import json
import os
from gesture_glide.mp_wrapper import MPWrapper
from gesture_glide.config import Config
from gesture_glide.utils import Observer, Observable


class GestureRecognizer(Observer, Observable):
    def __init__(self, config: Config, mp_wrapper: MPWrapper):
        super().__init__()
        self.config = config
        mp_wrapper.add_observer(self)

        config_path = 'gestures.json'
        if os.path.exists(config_path):
            with open(config_path, 'r') as file:
                try:
                    self.gesture_data = json.load(file)
                except json.JSONDecodeError:
                    self.gesture_data = {}
        else:
            self.gesture_data = {}

    def recognize_gesture(self, current_landmarks):
        for gesture_name, stored_landmarks in self.gesture_data.items():
            if self.compare_landmarks(current_landmarks, stored_landmarks):
                print(f"Erkannte Geste: {gesture_name}")
                break

    def update(self, observable, *args, **kwargs):
        current_landmarks = kwargs["results"].multi_hand_landmarks
        if current_landmarks is not None:
            self.recognize_gesture(current_landmarks)

    @staticmethod
    def compare_landmarks(current, stored, threshold=0.1):
        if len(current) != len(stored):
            return False

        for i in range(len(current)):
            cx, cy, cz = current[i]
            sx, sy, sz = stored[i]
            if abs(cx - sx) > threshold or abs(cy - sy) > threshold or abs(cz - sz) > threshold:
                return False

        return True
