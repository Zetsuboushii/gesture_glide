import logging
import platform
import subprocess
from gesture_glide.config import Config


class ApplicationShortcut:
    config: Config

    def __init__(self, config: Config):
        self.config = config
        self.application_window = None
        self.system = platform.system()
        self.init_scroll_backend()

    def init_scroll_backend(self):
        if self.system == 'Windows':
            self.init_windows_backend()
        elif self.system == 'Linux':
            self.init_linux_backend()
        else:
            logging.error(f"Unsupported OS: {self.system}")

    def init_windows_backend(self):
        try:
            import pygetwindow as gw
            self.gw = gw
            self.application_window = self.get_windows_window()
        except Exception as e:
            logging.error(e)

    def get_windows_window(self):
        try:
            acrobat_window = self.gw.getWindowsWithTitle('Acrobat')[0]
            if acrobat_window:
                return acrobat_window
        except Exception:
            logging.info("Acrobat Reader not found.")

        try:
            firefox_window = self.gw.getWindowsWithTitle('Mozilla Firefox')[0]
            if firefox_window:
                return firefox_window
        except Exception:
            logging.info("Firefox not found.")

        try:
            chromium_window = self.gw.getWindowsWithTitle('Chromium')[0]
            if chromium_window:
                return chromium_window
        except Exception:
            logging.info("Chromium not found.")

        try:
            intellij_window = self.gw.getWindowsWithTitle('IntelliJ IDEA')[0]
            if intellij_window:
                return intellij_window
        except Exception:
            logging.info("IntelliJ not found.")

        logging.warning("No supported application found.")
        return None

    def init_linux_backend(self):
        try:
            self.application_window = self.get_linux_window()
        except Exception as e:
            logging.error(e)

    def get_linux_window(self):
        try:
            acrobat_window = self.find_window_by_name("Acrobat Reader")
            if acrobat_window:
                return acrobat_window
        except Exception:
            logging.info("Acrobat Reader not found.")

        try:
            firefox_window = self.find_window_by_name("Firefox")
            if firefox_window:
                return firefox_window
        except Exception:
            logging.info("Firefox not found.")

        try:
            chromium_window = self.find_window_by_name("Chromium")
            if chromium_window:
                return chromium_window
        except Exception:
            logging.info("Chromium not found.")

        try:
            intellij_window = self.find_window_by_name("IntelliJ IDEA")
            if intellij_window:
                return intellij_window
        except Exception:
            logging.info("IntelliJ not found.")

        logging.warning("No supported application found.")
        return None

    def find_window_by_name(self, window_name: str):
        result = subprocess.run(['wmctrl', '-l'], capture_output=True, text=True)
        windows = result.stdout.splitlines()
        for window in windows:
            if window_name in window:
                return window.split()[0]  # Return window ID
        return None

    def execute(self, **kwargs):
        if self.application_window:
            self.scroll_window(**kwargs)
        else:
            logging.warning("No application window available for scrolling.")

    def scroll_window(self, **kwargs):
        if self.system == 'Windows':
            self.scroll_windows_window(**kwargs)
        elif self.system == 'Linux':
            self.scroll_linux_window(**kwargs)

    def scroll_windows_window(self, **kwargs):
        direction = kwargs.get('direction', 'down')
        scroll_amount = kwargs.get('amount', 3)

        # Bring the window to the foreground
        self.application_window.activate()

        # Simulate scrolling
        import pyautogui
        if direction == 'down':
            pyautogui.scroll(-scroll_amount * 100)
        elif direction == 'up':
            pyautogui.scroll(scroll_amount * 100)

    def scroll_linux_window(self, **kwargs):
        direction = kwargs.get('direction', 'down')
        scroll_amount = kwargs.get('amount', 3)
        window_id = self.application_window

        # Bring the window to the foreground
        subprocess.run(['wmctrl', '-ia', window_id])

        # Scroll using xdotool
        button = '5' if direction == 'down' else '4'
        for _ in range(scroll_amount):
            subprocess.run(['xdotool', 'windowactivate', '--sync', window_id, 'key', f'{button}'])
