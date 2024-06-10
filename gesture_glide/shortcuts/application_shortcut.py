import logging
from pywinauto import Desktop
from gesture_glide.config import Config


class ApplicationShortcut:
    config: Config

    def __init__(self, config: Config):
        self.config = config
        self.desktop = None
        self.application_window = None
        self.init_scroll_backend()

    def init_scroll_backend(self):
        try:
            self.desktop = Desktop(backend="uia")
            self.application_window = self.get_window()
        except Exception as e:
            logging.error(e)

    def get_window(self):
        try:
            # Check for Acrobat Reader window
            acrobat_window = self.desktop.window(class_name="AcrobatSDIWindow")
            if acrobat_window.exists():
                return acrobat_window
        except Exception as e:
            logging.info("Acrobat Reader not found.")

        try:
            # Check for Firefox window
            firefox_window = self.desktop.window(class_name="MozillaWindowClass")
            if firefox_window.exists():
                return firefox_window
        except Exception as e:
            logging.info("Firefox not found.")

        try:
            # Check for Chromium based windows
            chromium_window = self.desktop.window(class_name="Chrome_WidgetWin_1")
            if chromium_window.exists():
                return chromium_window
        except Exception as e:
            logging.info("Chromium not found.")

        try:
            # Check for IntelliJ based windows
            intellij_window = self.desktop.window(class_name="SunAwtFrame")
            if intellij_window.exists():
                return intellij_window
        except Exception as e:
            logging.info("IntelliJ not found.")

        logging.warning("No supported application found.")
        return None

    def execute(self, **kwargs):
        if self.application_window:
            self.scroll_window(**kwargs)
        else:
            logging.warning("No application window available for scrolling.")

    def scroll_window(self, **kwargs):
        # Implement scrolling functionality here
        pass
