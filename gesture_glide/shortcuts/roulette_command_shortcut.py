import logging
from gesture_glide.shortcuts.application_shortcut import ApplicationShortcut


class RouletteCommandShortcut(ApplicationShortcut):

    def execute(self, key: str):
        try:
            # enlarge, reduce or spin roulette section
            from pywinauto.keyboard import send_keys
            send_keys("{"+key+" down}{"+key+" up}")
        except Exception as e:
            logging.error(e)
