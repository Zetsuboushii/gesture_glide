import time
from threading import Thread, Event

from gesture_glide.camera_handler import CameraHandler
from gesture_glide.config import Config
from gesture_glide.gesture_interpreter import GestureInterpreter
from gesture_glide.gesture_recognizer import GestureRecognizer
from gesture_glide.gesture_writer import GestureWriter
from gesture_glide.mp_wrapper import MPWrapper
from gesture_glide.hand_movement_recognizer import HandMovementRecognizer


class EngineController:
    config: Config
    camera_handler: CameraHandler
    mp_wrapper: MPWrapper
    scroll_recognizer: HandMovementRecognizer
    gesture_interpreter: GestureInterpreter
    gesture_recognizer: GestureRecognizer
    gesture_writer: GestureWriter
    running_thread: Thread | None

    def __init__(self, config: Config):
        super().__init__()
        self.config = config
        self.camera_handler = CameraHandler()
        self.mp_wrapper = MPWrapper(self.camera_handler)
        self.scroll_recognizer = HandMovementRecognizer(self.mp_wrapper)
        self.gesture_recognizer = GestureRecognizer(config, self.mp_wrapper)
        self.gesture_interpreter = GestureInterpreter(self.config, self.mp_wrapper,
                                                      self.scroll_recognizer,self.gesture_recognizer)
        self.gesture_writer = GestureWriter(self.config, self.mp_wrapper)
        self.running_thread = None

    def run(self):
        self.running_thread = Thread(target=self.camera_handler.run)
        self.running_thread.start()
        self.gesture_interpreter.run()

    def stop(self):
        self.gesture_interpreter.stop()
        self.camera_handler.stop_event.set()
        if self.running_thread is not None:
            while self.running_thread.is_alive():
                self.running_thread.join(1)
                time.sleep(1)

    def capture(self):
        self.gesture_writer.capture_gesture("knecht")
