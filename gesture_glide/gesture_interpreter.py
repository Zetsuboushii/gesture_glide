import logging

from gesture_glide.config import Config
from gesture_glide.mp_wrapper import MPWrapper
from gesture_glide.hand_movement_recognizer import HandMovementRecognizer
from gesture_glide.shortcuts.generic_scroll_shortcut import GenericScrollShortcut
from gesture_glide.utils import Observer


class GestureInterpreter(Observer):
    config: Config

    def __init__(self, config: Config, mp_wrapper: MPWrapper, movement_recognizer: HandMovementRecognizer):
        self.config = config
        mp_wrapper.add_observer(self)
        movement_recognizer.add_observer(self)
        self.scroll_shortcut = GenericScrollShortcut(config)

    def run(self):
        self.scroll_shortcut.run()

    def stop(self):
        self.scroll_shortcut.stop()

    def update(self, observable, *args, **kwargs):
        scroll_command = kwargs.get("scroll_command")
        if scroll_command is not None:
            self.scroll_shortcut.execute(**kwargs)