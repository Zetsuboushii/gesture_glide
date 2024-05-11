import logging

from gesture_glide.config import Config
from gesture_glide.mp_wrapper import MPWrapper
from gesture_glide.recognized_gesture import RecognizedGesture, GestureType
from gesture_glide.scroll_recognizer import ScrollRecognizer
from gesture_glide.shortcuts.generic_scroll_shortcut import GenericScrollShortcut
from gesture_glide.utils import Observer


class GestureInterpreter(Observer):
    config: Config

    def __init__(self, config: Config, mp_wrapper: MPWrapper, scroll_recognizer: ScrollRecognizer):
        self.config = config
        mp_wrapper.add_observer(self)
        scroll_recognizer.add_observer(self)
        self.scroll_shortcut = GenericScrollShortcut(config)

    def update(self, observable, *args, **kwargs):
        scroll_command = kwargs.get("scroll_command")
        if scroll_command is not None:
            self.scroll_shortcut.execute(**kwargs)

    def get_shortcut_for_recognized_gesture(self, recognized_gesture: RecognizedGesture):
        match recognized_gesture.type:
            case GestureType.SCROLL:
                return GenericScrollShortcut(self.config)
            case _:
                raise NotImplementedError()
