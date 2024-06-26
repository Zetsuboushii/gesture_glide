# Autoren: Luke Grasser
import logging
from gesture_glide.shortcuts.application_shortcut import ApplicationShortcut


class MicrosoftOfficePowerPointCommandShortcut(ApplicationShortcut):

    # Method to execute a command with a given key
    def execute(self, key: str):
        self.get_current_window()  # Call to method that gets the current active window
        # Check if the active window is a PowerPoint window
        if self.active_window == self.desktop.window(class_name="PPTFrameClass"):
            try:
                from pywinauto.keyboard import send_keys  # Importing the send_keys function from pywinauto.keyboard
                # Simulate key press and release
                send_keys("{" + key + " down}{" + key + " up}")
            except Exception as e:
                logging.error(e)  # Log any exceptions that occur
