from tkinter import Tk, Frame, StringVar
from tkinter import ttk

import cv2
from PIL import ImageTk, Image

from gesture_glide.engine_controller import EngineController
from gesture_glide.utils import Observer
import threading

def setup_gui(root: Tk, controller: EngineController):
    class DataHandler(Observer):
        def __init__(self):
            super().__init__()
            self.image_label = None
            self.latest_frame = None
            self.updating_image = False

        def update(self, observable, *args, **kwargs):
            nonlocal frame_rate
            frame_rate.set(kwargs.get("frame_rate") or "N/A")
            image_frame = kwargs.get("scroll_overlay")
            if image_frame is not None:
                self.latest_frame = image_frame
                if not self.updating_image:
                    self.updating_image = True
                    threading.Thread(target=self.update_image).start()

        def update_image(self):
            while self.latest_frame is not None:
                image_frame = self.latest_frame
                self.latest_frame = None

                # Convert the frame from BGR to RGB
                image_frame = cv2.cvtColor(image_frame, cv2.COLOR_BGR2RGB)
                # Convert the frame from a numpy array to a PIL Image
                image = Image.fromarray(image_frame)
                image_tk = ImageTk.PhotoImage(image)

                # Update the image label in the main thread
                root.after(0, self.update_image_label, image_tk)

        def update_image_label(self, image_tk):
            if self.image_label is None:
                self.image_label = ttk.Label(frame, image=image_tk)
                self.image_label.grid(row=1)
            else:
                self.image_label.configure(image=image_tk)
            self.image_label.image = image_tk
            self.updating_image = False

    frame_rate = StringVar()
    frame = Frame(root)
    frame.grid()

    ttk.Label(frame, text="FPS").grid(column=0, row=0)
    ttk.Label(frame, textvariable=frame_rate).grid(column=1, row=0)

    ttk.Button(frame, text="Start", command=lambda: controller.start()).grid(column=0, row=2)
    ttk.Button(frame, text="Stop", command=lambda: controller.stop()).grid(column=1, row=2)
    ttk.Button(frame, text="Quit", command=lambda: exit_program(root, controller)).grid(column=2, row=2)

    handler = DataHandler()
    controller.camera_handler.add_observer(handler)
    controller.scroll_recognizer.add_observer(handler)

def exit_program(root: Tk, controller: EngineController):
    controller.stop()
    controller.join(1)
    root.destroy()
    exit(0)

def run_gui(controller: EngineController):
    root = Tk()
    setup_gui(root, controller)
    root.mainloop()
