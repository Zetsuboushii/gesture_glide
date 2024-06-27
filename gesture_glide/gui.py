import threading
import os
from tkinter import Tk, Frame, StringVar, ttk, Entry, HORIZONTAL, Scale
import cv2
from PIL import ImageTk, Image
from gesture_glide.engine_controller import EngineController
from gesture_glide.utils import Observer, GestureMode


def setup_gui(root: Tk, controller: EngineController):
    class DataHandler(Observer):
        def __init__(self):
            super().__init__()
            self.image_label = None
            self.latest_frame = None
            self.updating_image = False

        def update(self, observable, *args, **kwargs):
            if controller.camera_handler.stop_event.is_set():
                return
            nonlocal frame_rate
            fr_rate = kwargs.get('frame_rate')
            mode: GestureMode | None = kwargs.get("gesture_mode")
            if fr_rate is not None:
                fr_rate = format(fr_rate, '.2f') if fr_rate is not None else None
                try:
                    frame_rate.set(f"{fr_rate}" or "N/A")
                except RuntimeError:
                    return  # Main thread not available anymore
            image_frame = kwargs.get("scroll_overlay")
            if image_frame is not None:
                self.latest_frame = image_frame
                if not self.updating_image:
                    self.updating_image = True
                    threading.Thread(target=self.update_image).start()
            if mode is not None:
                gesture_mode.set(mode.name)

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
                self.image_label.grid(column=0, row=0)
            else:
                self.image_label.configure(image=image_tk)
            self.image_label.image = image_tk
            self.updating_image = False

    def capture(controller: EngineController, gesture_name: StringVar):
        gesture_name_value = gesture_name.get()
        if gesture_name_value:
            controller.capture(gesture_name_value)

    def apply_user_settings():
        controller.apply_user_settings(
            spd_thrld_slider.get() / 100.0,
            spread_thrld_slider.get() / 100.0,
            scroll_speed_slider.get() / 100.0
        )

    def delete_gestures_file():
        try:
            os.remove("gestures.json")
            print("gestures.json deleted successfully")
        except FileNotFoundError:
            print("gestures.json not found")

    frame_rate = StringVar()
    gesture_mode = StringVar()
    frame = Frame(root, width=500, height=500)
    frame.grid()
    data_container = Frame(frame, width=300)
    data_container.grid(column=0, row=1, sticky="W")

    gesture_name = StringVar()
    ttk.Label(data_container, text="Gesture Name").grid(column=0, row=2, sticky="W")
    gesture_name_entry = Entry(data_container, textvariable=gesture_name)
    gesture_name_entry.grid(column=1, row=2, sticky="W")

    settings = Frame(frame, width=600)
    settings.grid()
    ttk.Label(settings, text="Speed threshold").grid(column=0, row=0, sticky="W")
    spd_thrld_slider = Scale(settings, from_=0, to=200, orient=HORIZONTAL)
    spd_thrld_slider.set(100)
    spd_thrld_slider.grid(column=1, row=0, sticky="W")

    ttk.Label(settings, text="Spread threshold").grid(column=0, row=1, sticky="W")
    spread_thrld_slider = Scale(settings, from_=0, to=200, orient=HORIZONTAL)
    spread_thrld_slider.set(100)
    spread_thrld_slider.grid(column=1, row=1, sticky="W")

    ttk.Label(settings, text="Scrolling speed").grid(column=0, row=2, sticky="W")
    scroll_speed_slider = Scale(settings, from_=0, to=200, orient=HORIZONTAL)
    scroll_speed_slider.set(100)
    scroll_speed_slider.grid(column=1, row=2, sticky="W")

    ttk.Label(data_container, text="FPS").grid(column=0, row=0, sticky="W")
    ttk.Label(data_container, textvariable=frame_rate).grid(column=1, row=0, sticky="W")

    ttk.Label(data_container, textvariable=gesture_mode).grid(column=2, row=0, sticky="W")

    ttk.Button(data_container, text="Start", command=lambda: run(controller)).grid(column=0, row=1, sticky="W")
    ttk.Button(data_container, text="Stop", command=lambda: stop(controller)).grid(column=1, row=1, sticky="W")
    ttk.Button(data_container, text="Quit", command=lambda: exit_program(root, controller)).grid(column=2, row=1,
                                                                                                 sticky="W")
    ttk.Button(data_container, text="Capture", command=lambda: capture(controller, gesture_name)).grid(column=4, row=1,
                                                                                                       sticky="W")
    ttk.Button(data_container, text="Apply", command=apply_user_settings).grid(column=5, row=1, sticky="W")
    ttk.Button(data_container, text="Delete saved gestures", command=delete_gestures_file).grid(column=6, row=1,
                                                                                               sticky="W")

    handler = DataHandler()
    controller.camera_handler.add_observer(handler)
    controller.mp_wrapper.add_observer(handler)
    controller.scroll_recognizer.add_observer(handler)
    controller.gesture_interpreter.add_observer(handler)


def exit_program(root: Tk, controller: EngineController):
    controller.stop()
    root.destroy()


def run(controller: EngineController):
    controller.run()


def stop(controller: EngineController):
    controller.stop()


def run_gui(controller: EngineController):
    root = Tk()
    setup_gui(root, controller)
    root.mainloop()
