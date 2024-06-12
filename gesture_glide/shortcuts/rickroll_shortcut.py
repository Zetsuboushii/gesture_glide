import time
import pywhatkit
import logging

from gesture_glide.shortcuts.application_shortcut import ApplicationShortcut


class RickRollShortcut(ApplicationShortcut):
    """"opening Rick Roll with autoplay through recognized handgesture"""

    def execute(self):
        try:
            pywhatkit.playonyt("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
            print("You're getting Rick'n'Rolled!!")
            time.sleep(5)
            from pywinauto.keyboard import send_keys
            send_keys("{SPACE}")
        except Exception as e:
            logging.error(e)

