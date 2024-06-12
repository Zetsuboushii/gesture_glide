import json
import os
import logging
from gesture_glide.mp_wrapper import MPWrapper
from gesture_glide.config import Config
from gesture_glide.utils import Observer, Observable, RecognizedGesture


class GestureRecognizer(Observer, Observable):
    """Recognizer of gestures based on hand landmarks, but no interpretation of them."""
    def __init__(self, config: Config, mp_wrapper: MPWrapper):
        super().__init__()
        self.config = config
        self.gesture_data = self.load_gesture_data('gestures.json')
        mp_wrapper.add_observer(self)

    @staticmethod
    def load_gesture_data(config_path: str) -> dict:
        if os.path.exists(config_path):
            with open(config_path, 'r') as file:
                try:
                    return json.load(file)
                except json.JSONDecodeError:
                    logging.error(f"Error decoding JSON from {config_path}")
                    return {}
        return {}

    def recognize_gesture(self, current_landmarks):
        normalized_current = self.normalize_landmarks(current_landmarks)
        for gesture_name, stored_landmarks in self.gesture_data.items():
            normalized_stored = self.normalize_landmarks(stored_landmarks)
            if self.compare_landmarks(normalized_current, normalized_stored):
                recognized_gesture = self.map_gesture_name_to_recognized_gesture(gesture_name)
                if recognized_gesture:
                    logging.info(f"Erkannte Geste: {gesture_name}")
                    self.notify_observers(recognized_gesture=recognized_gesture)
                break

    @staticmethod
    def map_gesture_name_to_recognized_gesture(gesture_name: str) -> RecognizedGesture:
        mapping = {
            "OpenRoulette": RecognizedGesture.OPEN_ROULETTE,
            "EnlargeRouletteField": RecognizedGesture.ROULETTE_PLUS,
            "ReduceRouletteField": RecognizedGesture.ROULETTE_MINUS,
            "RR": RecognizedGesture.RICK_ROLL,
        }
        return mapping.get(gesture_name)

    def update(self, observable, *args, **kwargs):
        multi_hand_landmarks = kwargs.get("results").multi_hand_landmarks
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
    def compare_landmarks(current, stored, threshold=0.125):
        if len(current) != len(stored):
            return False
        for current_point, stored_point in zip(current, stored):
            if any(abs(c - s) > threshold for c, s in zip(current_point, stored_point)):
                return False
        return True
