import json
import os
from gesture_glide.mp_wrapper import MPWrapper
from gesture_glide.config import Config
from gesture_glide.gesture_interpreter import GestureInterpreter
from gesture_glide.engine_controller import EngineController
from gesture_glide.recognized_gesture import RecognizedGesture, GestureType


class GestureRecognizer:
    def __init__(self, mp_wrapper: MPWrapper):
        self.config = Config()
        self.mp_wrapper = mp_wrapper
        self.gesture_interpreter = GestureInterpreter(self.config, self.mp_wrapper)
        self.engine_controller = EngineController(self.config)

    def recognize_gesture(self):
        if os.path.exists('gesture_config.json'):
            with open('gesture_config.json', 'r') as file:
                try:
                    gesture_data = json.load(file)
                except json.JSONDecodeError:
                    gesture_data = {}
        else:
            gesture_data = {}

        def recognition_callback(current_landmarks):
            for gesture_name, stored_landmarks in gesture_data.items():
                if self.compare_landmarks(current_landmarks, stored_landmarks):
                    print(f"Erkannte Geste: {gesture_name}")
                    recognized_gesture = RecognizedGesture(GestureType(gesture_name), {})
                    shortcut = self.gesture_interpreter.get_shortcut_for_recognized_gesture(recognized_gesture)
                    shortcut.execute()
                    break

        self.mp_wrapper.set_recognition_callback(recognition_callback)
        print("Recognition started. Press 'q' to quit")
        self.engine_controller.run()

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
