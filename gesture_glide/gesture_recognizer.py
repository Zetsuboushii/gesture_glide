# Autoren: Isabel Barbu,Nick Büttner,Miguel Themann,Luke Grasser
import json
import os
import logging
from gesture_glide.mp_wrapper import MPWrapper
from gesture_glide.config import Config
from gesture_glide.utils import Observer, Observable, RecognizedGesture


class GestureRecognizer(Observer, Observable):
    """Recognizer of gestures based on hand landmarks, but no interpretation of them."""

    # Initializing the GestureRecognizer class
    def __init__(self, config: Config, mp_wrapper: MPWrapper):
        super().__init__()  # Initialize the parent classes
        self.config = config  # Storing configuration
        self.gesture_data = self.load_gesture_data('gestures.json')  # Loading gesture data from JSON file
        mp_wrapper.add_observer(self)  # Adding self as an observer to mp_wrapper

    # Static method to load gesture data from a JSON file
    @staticmethod
    def load_gesture_data(config_path: str) -> dict:
        if os.path.exists(config_path):  # Check if the config path exists
            with open(config_path, 'r') as file:  # Open the JSON file
                try:
                    return json.load(file)  # Load and return the JSON data
                except json.JSONDecodeError:
                    logging.error(f"Error decoding JSON from {config_path}")  # Log error if JSON decoding fails
                    return {}
        return {}  # Return an empty dictionary if file does not exist

    # Method to recognize gestures based on current landmarks
    def recognize_gesture(self, current_landmarks):
        normalized_current = self.normalize_landmarks(current_landmarks)  # Normalize current landmarks
        for gesture_name, stored_landmarks in self.gesture_data.items():
            normalized_stored = self.normalize_landmarks(stored_landmarks)  # Normalize stored landmarks
            if self.compare_landmarks(normalized_current, normalized_stored):  # Compare current and stored landmarks
                recognized_gesture = self.map_gesture_name_to_recognized_gesture(gesture_name)
                if recognized_gesture:
                    logging.info(f"Recognized Gesture: {gesture_name}")  # Log the recognized gesture
                    self.notify_observers(
                        recognized_gesture=recognized_gesture)  # Notify observers of the recognized gesture
                break

    # Static method to map gesture names to recognized gestures
    @staticmethod
    def map_gesture_name_to_recognized_gesture(gesture_name: str) -> RecognizedGesture:
        mapping = {
            "OpenRoulette": RecognizedGesture.OPEN_ROULETTE,
            "EnlargeRouletteField": RecognizedGesture.ROULETTE_PLUS,
            "ReduceRouletteField": RecognizedGesture.ROULETTE_MINUS,
            "RR": RecognizedGesture.RICK_ROLL,
        }
        return mapping.get(gesture_name)  # Return the mapped recognized gesture

    # Method to update based on observed events
    def update(self, observable, *args, **kwargs):
        multi_hand_landmarks = kwargs.get("results").multi_hand_landmarks  # Get multi-hand landmarks from kwargs
        if multi_hand_landmarks:
            for hand_landmarks in multi_hand_landmarks:
                formatted_landmarks = self.format_landmarks(hand_landmarks)  # Format hand landmarks
                self.recognize_gesture(formatted_landmarks)  # Recognize gesture from formatted landmarks

    # Static method to format hand landmarks
    @staticmethod
    def format_landmarks(hand_landmarks):
        return [(lm.x, lm.y, lm.z) for lm in
                hand_landmarks.landmark]  # Return a list of tuples with landmark coordinates

    # Static method to normalize landmarks based on the wrist position
    @staticmethod
    def normalize_landmarks(landmarks):
        wrist = landmarks[0]  # Get the wrist coordinates (first landmark)
        return [(lm[0] - wrist[0], lm[1] - wrist[1], lm[2] - wrist[2]) for lm in
                landmarks]  # Normalize landmarks relative to the wrist

    # Static method to compare current and stored landmarks with a threshold
    @staticmethod
    def compare_landmarks(current, stored, threshold=0.1):
        if len(current) != len(stored):  # Check if the number of points in current and stored landmarks are equal
            return False
        for current_point, stored_point in zip(current, stored):
            if any(abs(c - s) > threshold for c, s in
                   zip(current_point, stored_point)):  # Compare each point with a threshold
                return False
        return True  # Return True if all points are within the threshold
