import logging
from pywinauto.keyboard import send_keys
from gesture_glide.shortcuts.application_shortcut import ApplicationShortcut


class RouletteCommandShortcut(ApplicationShortcut):

    def execute(self, key: str):
        try:
            send_keys(key)
        except Exception as e:
            logging.error(e)
