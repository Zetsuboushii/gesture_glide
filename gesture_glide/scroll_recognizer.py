from gesture_glide.mp_wrapper import MPWrapper
from gesture_glide.utils import Observer, Observable


class ScrollRecognizer(Observer, Observable):
    def __init__(self, mp_wrapper: MPWrapper):
        super().__init__()
        mp_wrapper.add_observer(self)

    def update(self, observable, *args, **kwargs):
        self.notify_observers(None)
