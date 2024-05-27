import json
import os
from gesture_glide.mp_wrapper import MPWrapper
from gesture_glide.config import Config
from gesture_glide.utils import Observer, Observable


class GestureRecognizer(Observer, Observable):
    def __init__(self, config: Config, mp_wrapper: MPWrapper):
        super().__init__()
        self.config = config
        self.mp_wrapper = mp_wrapper
        mp_wrapper.add_observer(self)

        if os.path.exists('gesture_config.json'):
            with open('gesture_config.json', 'r') as file:
                try:
                    self.gesture_data = json.load(file)
                except json.JSONDecodeError:
                    self.gesture_data = {}
        else:
            self.gesture_data = {}

    def recognize_gesture(self):
        def recognition_callback(current_landmarks):
            for gesture_name, stored_landmarks in self.gesture_data.items():
                if self.compare_landmarks(current_landmarks, stored_landmarks):
                    print(f"Erkannte Geste: {gesture_name}")
                    break
        # TODO
        # self.mp_wrapper.set_recognition_callback(recognition_callback)
        print("Recognition started. Press 'q' to quit")

    def update(self, observable, *args, **kwargs):
        self.recognize_gesture()

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
