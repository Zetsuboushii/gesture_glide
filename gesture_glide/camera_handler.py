import time

import cv2

from gesture_glide.utils import Observable


class CameraHandler(Observable):
    def __init__(self):
        super().__init__()

    def run(self):
        capture = cv2.VideoCapture(0)
        while True:
            success, frame = capture.read()
            cv2.imshow('Capture', frame)
            self.notify_observers(frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
