# Autoren: Luke Grasser
import logging
from gesture_glide.shortcuts.application_shortcut import ApplicationShortcut


class MicrosoftOfficePowerPointCommandShortcut(ApplicationShortcut):

    def execute(self, key: str):
        self.get_current_window()
        if self.active_window == self.desktop.window(class_name="PPTFrameClass"):
            try:
                # enlarge, reduce or spin roulette section
                from pywinauto.keyboard import send_keys
                send_keys("{"+key+" down}{"+key+" up}")
            except Exception as e:
                logging.error(e)
