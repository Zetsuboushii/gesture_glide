import logging

from gesture_glide.config import Config


class ApplicationShortcut:
    config: Config

    def __init__(self, config: Config):
        self.config = config
        self.desktop = None
        self.pdf_window = None
        self.init_scroll_backend()

    def init_scroll_backend(self):
        try:
            from pywinauto import Desktop
            self.desktop = Desktop(backend="uia")
            self.pdf_window = self.desktop.window(class_name="AcrobatSDIWindow")
        except Exception as e:
            logging.error(e)

    def execute(self, **kwargs):
        raise NotImplementedError()
