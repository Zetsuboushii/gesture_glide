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
    stop_event: Event

    def __init__(self):
        super().__init__()
        self.frame_count = 0
        self.stop_event = Event()

    def run(self):
        self.stop_event.clear()
        capture = cv2.VideoCapture(0)
        start_time = time.time()
        last_frame_time = start_time
        frame_rate = None
        while not self.stop_event.is_set():
            try:
                success, frame = capture.read()
            except cv2.error as e:
                success = False
            if not success:
                continue # Recheck stop event in case thread is supposed to stop
            metadata = FrameMetadata(width=frame.shape[0], height=frame.shape[1])
            time_from_last_frame = time.time() - last_frame_time
            frame_rate = 1 / time_from_last_frame if time_from_last_frame > 0 else None
            self.notify_observers(frame=frame, metadata=metadata, frame_rate=frame_rate)
            self.frame_count += 1
            last_frame_time = time.time()
            print("\rFPS:", frame_rate, end="")
        seconds = time.time() - start_time
        print(f"\nRead {self.frame_count} frames in {seconds} ({frame_rate :.2f} fps).")
        capture.release()
        cv2.destroyAllWindows()
