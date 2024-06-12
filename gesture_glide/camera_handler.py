# Autoren: Nick Büttner,Miguel Themann
import time
from threading import Event

import cv2

from gesture_glide.utils import Observable


class FrameMetadata:
    width: int
    height: int

    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height


class CameraHandler(Observable):
    """Entrypoint for camera data (reads stream and notifies observers with frame data)."""
    stop_event: Event

    def __init__(self):
        super().__init__()
        self.frame_count = 0
        self.stop_event = Event()

    def run(self):
        self.stop_event.clear()
        capture = cv2.VideoCapture(0)
        while not self.stop_event.is_set():
            try:
                success, frame = capture.read()
            except cv2.error as e:
                success = False
            if not success:
                continue  # Recheck stop event in case thread is supposed to stop
            metadata = FrameMetadata(width=frame.shape[0], height=frame.shape[1])
            self.notify_observers(frame=frame, metadata=metadata)
            self.frame_count += 1
        capture.release()
        cv2.destroyAllWindows()
