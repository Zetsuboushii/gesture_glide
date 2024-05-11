from gesture_glide.scroll_recognizer import ScrollData
from gesture_glide.shortcuts.application_shortcut import ApplicationShortcut


class GenericScrollShortcut(ApplicationShortcut):
    def execute(self, **kwargs):
        self.scroll_action(kwargs["scroll_command"])

    def scroll_action(self, command: ScrollData):
        # Simulates mouse wheel actions based on detected hand movement direction
        try:
            for _ in range(10):
                self.pdf_window.wheel_mouse_input(wheel_dist=command.direction.value)
        except Exception as e:
            print(e)
