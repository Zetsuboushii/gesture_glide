from gesture_glide.mp_wrapper import MPWrapper
from gesture_glide.scroll_recognizer import ScrollRecognizer


class GestureInterpreter:
    def __init__(self, mp_wrapper: MPWrapper, scroll_recognizer: ScrollRecognizer):
        mp_wrapper.add_observer(mp_wrapper)
        scroll_recognizer.add_observer(scroll_recognizer)