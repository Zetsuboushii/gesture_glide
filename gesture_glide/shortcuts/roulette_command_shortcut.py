import logging
import pyautogui
from gesture_glide.shortcuts.application_shortcut import ApplicationShortcut


class RouletteCommandShortcut(ApplicationShortcut):

    def execute(self, key: str):
        try:
            pyautogui.press(key)
        except Exception as e:
            logging.error(e)
