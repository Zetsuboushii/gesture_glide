from threading import Thread, Event

from gesture_glide.camera_handler import CameraHandler
from gesture_glide.config import Config
from gesture_glide.gesture_interpreter import GestureInterpreter
from gesture_glide.mp_wrapper import MPWrapper
from gesture_glide.hand_movement_recognizer import HandMovementRecognizer


class EngineController:
    config: Config
    camera_handler: CameraHandler
    mp_wrapper: MPWrapper
    scroll_recognizer: HandMovementRecognizer
    gesture_interpreter: GestureInterpreter
    running_thread: Thread | None

    def __init__(self, config: Config):
        super().__init__()
        self.config = config
        self.camera_handler = CameraHandler()
        self.mp_wrapper = MPWrapper(self.camera_handler)
        self.scroll_recognizer = HandMovementRecognizer(self.mp_wrapper)
        self.gesture_interpreter = GestureInterpreter(self.config, self.mp_wrapper, self.scroll_recognizer)
        self.stop_event = Event()
        self.running_thread = None

    def run(self):
        self.stop_event.clear()
        self.running_thread = Thread(target=lambda: self.camera_handler.run(self.stop_event))
        self.running_thread.start()

    def stop(self):
        self.stop_event.set()
        if self.running_thread is not None:
            self.running_thread.join()