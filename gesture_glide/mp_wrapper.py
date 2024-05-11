import cv2

from gesture_glide.camera_handler import CameraHandler
from gesture_glide.utils import Observer, Observable
import mediapipe as mp


class MPWrapper(Observer, Observable):
    def __init__(self, camera_handler: CameraHandler):
        super().__init__()
        camera_handler.add_observer(self)
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands()

    def update(self, observable, *args, **kwargs):
        frame = kwargs["frame"]
        frame = cv2.cvtColor(cv2.flip(frame, 1), cv2.COLOR_BGR2RGB)
        results = self.hands.process(frame)
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR) # TODO: Remove if appropriate
        # Multihand landmarks -> hand landmarks -> landmark[x, y, z]
        self.notify_observers(metadata=kwargs["metadata"], results=results, frame=frame)