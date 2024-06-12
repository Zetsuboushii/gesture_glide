import math
import time
from threading import Event, Thread

from gesture_glide.config import Config
from gesture_glide.hand_movement_recognizer import ScrollData
from gesture_glide.shortcuts.application_shortcut import ApplicationShortcut


class GenericScrollShortcut(ApplicationShortcut):
    scrolling: Event
    scroll_data: ScrollData | None
    terminate: Event

    def __init__(self, config: Config):
        super().__init__(config)
        self.scrolling = Event()
        self.terminate = Event()
        self.scroll_data = None

    def execute(self, **kwargs):
        """Set scroll command to be executed by running scroll loop."""
        scroll_command = kwargs["scroll_command"]
        self.scroll_data = scroll_command
        if scroll_command is not None:
            self.scrolling.set()
        else:
            self.scrolling.clear()

    def run(self):
        """Execute scroll loop in separate thread"""
        self.terminate.clear()
        Thread(target=self.run_scroll_loop).start()

    def stop(self):
        """Instruct scroll loop to terminate."""
        self.terminate.set()

    def run_scroll_loop(self):
        """Execute scroll loop (blocking). Loop is responsible for decoupling scroll commands (esp. because of calculation FPS) and their execution."""
        while not self.terminate.is_set():
            if self.scrolling.is_set():
                if self.scroll_data is not None:
                    self.scroll_action(self.scroll_data)
                    self.scroll_data = None
            time.sleep(0.1)

    def scroll_action(self, command: ScrollData):
        # Simulates mouse wheel actions based on detected hand movement direction
        try:
            for _ in range(10):
                base = 2
                speed = math.ceil(1 if command.speed <= 0.4 else base ** (command.speed * 2))
                self.application_window.wheel_mouse_input(wheel_dist=-command.direction.value * speed)
        except Exception as e:
            print(e)
