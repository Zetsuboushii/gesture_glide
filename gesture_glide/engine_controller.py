from gesture_glide.camera_handler import CameraHandler
from gesture_glide.gesture_interpreter import GestureInterpreter
from gesture_glide.mp_wrapper import MPWrapper
from gesture_glide.scroll_recognizer import ScrollRecognizer


class EngineController:
    camera_handler: CameraHandler
    mp_wrapper: MPWrapper
    scroll_recognizer: ScrollRecognizer
    gesture_interpreter: GestureInterpreter

    def __init__(self):
        self.camera_handler = CameraHandler()
        self.mp_wrapper = MPWrapper(self.camera_handler)
        self.scroll_recognizer = ScrollRecognizer(self.mp_wrapper)
        self.gesture_interpreter = GestureInterpreter(self.mp_wrapper, self.scroll_recognizer)

    def run(self):
        self.camera_handler.run()
