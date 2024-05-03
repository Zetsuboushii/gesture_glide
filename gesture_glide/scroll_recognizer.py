from gesture_glide.mp_wrapper import MPWrapper
from gesture_glide.utils import Observer, Observable


class ScrollRecognizer(Observer, Observable):
    def __init__(self, mp_wrapper: MPWrapper):
        super().__init__()
        mp_wrapper.add_observer(self)

    def update(self, observable, *args, **kwargs):
        metadata = kwargs["metadata"]
        width = metadata["width"]
        height = metadata["height"]
        multihand_landmarks = kwargs["multihand_landmarks"]
        command = ScrollData(1, 200, 1)
        self.notify_observers(scroll_command=command)

class ScrollData:
    direction: int
    distance: float
    # seconds
    duration: float

    def __init__(self, direction: int, distance: float, duration: float):
        self.direction = direction
        self.distance = distance
        self.duration = duration