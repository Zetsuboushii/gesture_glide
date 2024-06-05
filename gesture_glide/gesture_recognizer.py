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
        normalized_current = self.normalize_landmarks(current_landmarks)
        for gesture_name, stored_landmarks in self.gesture_data.items():
            normalized_stored = self.normalize_landmarks(stored_landmarks)
            if self.compare_landmarks(normalized_current, normalized_stored):
                print(f"Erkannte Geste: {gesture_name}")
                break

    def update(self, observable, *args, **kwargs):
        multi_hand_landmarks = kwargs["results"].multi_hand_landmarks
        if multi_hand_landmarks:
            for hand_landmarks in multi_hand_landmarks:
                formatted_landmarks = self.format_landmarks(hand_landmarks)
                self.recognize_gesture(formatted_landmarks)

    @staticmethod
    def format_landmarks(hand_landmarks):
        return [(lm.x, lm.y, lm.z) for lm in hand_landmarks.landmark]

    @staticmethod
    def normalize_landmarks(landmarks):
        wrist = landmarks[0]
        return [(lm[0] - wrist[0], lm[1] - wrist[1], lm[2] - wrist[2]) for lm in landmarks]

    @staticmethod
    def compare_landmarks(current, stored, threshold=0.1):
        if len(current) != len(stored):
            # print(f"Landmark lengths differ: {len(current)} != {len(stored)}")
            return False

        for i in range(len(current)):
            cx, cy, cz = current[i]
            sx, sy, sz = stored[i]
            if abs(cx - sx) > threshold or abs(cy - sy) > threshold or abs(cz - sz) > threshold:
                # print(f"Landmarks differ at index {i}: current=({cx}, {cy}, {cz}), stored=({sx}, {sy}, {sz})")
                return False

        return True
