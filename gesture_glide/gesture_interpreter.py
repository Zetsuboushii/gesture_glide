from gesture_glide.mp_wrapper import MPWrapper
from gesture_glide.scroll_recognizer import ScrollRecognizer
from gesture_glide.utils import Observer


class GestureInterpreter(Observer):
    def __init__(self, mp_wrapper: MPWrapper, scroll_recognizer: ScrollRecognizer):
        mp_wrapper.add_observer(self)
        scroll_recognizer.add_observer(self)

    def update(self, observable, *args, **kwargs):
        pass
