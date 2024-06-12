import ctypes
import logging
from gesture_glide.config import Config


class ApplicationShortcut:
    config: Config

    def __init__(self, config: Config):
        self.config = config
        self.desktop = None
        self.init_scroll_backend()
        self.active_window = None
        self.last_active_window = None

    # get the current window to apply shortcuts/ commands on it
    def get_current_window(self):
        # TODO: Delete redundant imports
        # for mac "support" as library isn't supported
        from pywinauto import Desktop
        active_window_handle = ctypes.windll.user32.GetForegroundWindow()
        self.active_window = Desktop(backend="uia").window(handle=active_window_handle)


    def switch_to_previous_screen(self):
        if self.last_active_window:
            print("Switched to ", self.last_active_window)
            self.last_active_window.set_focus()


    def init_scroll_backend(self):
        try:
            # TODO: Delete redundant imports (2)
            # for mac "support" as library isn't supported
            from pywinauto import Desktop
            self.desktop = Desktop(backend="uia")
        except Exception as e:
            logging.error(e)

    def execute(self, **kwargs):
        raise NotImplementedError()
