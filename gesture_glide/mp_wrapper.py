from gesture_glide.camera_handler import CameraHandler
from gesture_glide.utils import Observer, Observable


class MPWrapper(Observer, Observable):
    def __init__(self, camera_handler: CameraHandler):
        super().__init__()
        camera_handler.add_observer(self)

    def update(self, observable, *args, **kwargs):
        pass
