import logging
from gesture_glide.shortcuts.application_shortcut import ApplicationShortcut


class RouletteOpenShortcut(ApplicationShortcut):
    def execute(self):
        self.get_current_window()
        self.last_active_window = self.active_window
        self.spin_roulette()

    def spin_roulette(self):
        try:
            roulette = self.desktop.window(class_name="GlassWndClass-GlassWindowClass-2")
            roulette.set_focus()
        except Exception as e:
            logging.error(e)
