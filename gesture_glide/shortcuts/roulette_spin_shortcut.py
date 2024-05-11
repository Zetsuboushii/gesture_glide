import logging

from gesture_glide.shortcuts.application_shortcut import ApplicationShortcut


class RouletteSpinShortcut(ApplicationShortcut):
    def execute(self):
        self.spin_roulette()

    def spin_roulette(self):
        try:
            roulette = self.desktop.window(class_name="GlassWndClass-GlassWindowClass-2")
            roulette.set_focus()
            send_keys("{SPACE}")
        except Exception as e:
            logging.error(e)
