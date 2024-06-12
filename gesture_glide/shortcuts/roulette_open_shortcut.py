# Autoren: Nick Büttner,Miguel Themann,Luke Grasser
import logging
from gesture_glide.shortcuts.application_shortcut import ApplicationShortcut


class RouletteOpenShortcut(ApplicationShortcut):
    def execute(self):
        self.get_current_window()
        # remember the last active window before switching to roulette, to return to it after the user is done with
        # the roulette
        self.last_active_window = self.active_window
        self.set_focus_to_roulette()

    def set_focus_to_roulette(self):
        try:
            # to identify the roulette app the windows class name is used because the app has no name set by the devs.
            roulette = self.desktop.window(class_name="GlassWndClass-GlassWindowClass-2")
            roulette.set_focus()
        except Exception as e:
            logging.error(e)
