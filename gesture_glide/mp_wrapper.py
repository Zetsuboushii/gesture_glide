from gesture_glide.camera_handler import CameraHandler
from gesture_glide.utils import Observer, Observable


class MPWrapper(Observer, Observable):
    def __init__(self, camera_handler: CameraHandler):
        super().__init__()
        camera_handler.add_observer(self)

    def update(self, observable, *args, **kwargs):
        frame = kwargs["frame"]
        metadata = {
            "width": frame.shape[0],
            "height": frame.shape[1]
        }
        # Multihand landmarks -> hand landmarks -> landmark[x, y, z]
        landmarks = []
        self.notify_observers(metadata=metadata, multihand_landmarks=landmarks)