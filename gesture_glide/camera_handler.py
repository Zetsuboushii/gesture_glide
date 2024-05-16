import threading
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
        self.frame_count = 0

    def run(self, stop_event: threading.Event):
        capture = cv2.VideoCapture(0)
        start_time = time.time()
        last_frame_time = start_time
        while not stop_event.is_set():
            success, frame = capture.read()
            metadata = FrameMetadata(width=frame.shape[0], height=frame.shape[1])
            time_from_last_frame = time.time() - last_frame_time
            frame_rate = 1 / time_from_last_frame
            self.notify_observers(frame=frame, metadata=metadata, frame_rate=frame_rate)
            self.frame_count += 1
            last_frame_time = time.time()
            print("\rFPS:", frame_rate, end="")
            if cv2.waitKey(1) & 0xFF == ord('q'):
                seconds = time.time() - start_time
                print(f"\nRead {self.frame_count} frames in {seconds} ({frame_rate :.2f} fps).")
                break
