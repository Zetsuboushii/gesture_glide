import time

import cv2

from gesture_glide.utils import Observable

class FrameMetadata:
    width: int
    height: int

    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height

class CameraHandler(Observable):
    def __init__(self):
        super().__init__()

    def run(self):
        capture = cv2.VideoCapture(0)
        while True:
            success, frame = capture.read()
            cv2.imshow('Capture', frame)
            metadata = FrameMetadata(width=frame.shape[0], height=frame.shape[1])
            self.notify_observers(frame=frame, metadata=metadata)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
