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
        scroll_command = kwargs["scroll_command"]
        self.scroll_data = scroll_command
        if scroll_command is not None:
            self.scrolling.set()
        else:
            self.scrolling.clear()

    def run(self):
        self.terminate.clear()
        Thread(target=self.run_scroll_loop).start()

    def stop(self):
        self.terminate.set()

    def run_scroll_loop(self):
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
                self.pdf_window.wheel_mouse_input(wheel_dist=-command.direction.value)
        except Exception as e:
            print(e)
