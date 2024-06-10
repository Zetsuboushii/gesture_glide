import ctypes

from pywinauto import Desktop
from pywinauto.keyboard import send_keys
import pywinauto.mouse
import time


def spinRouelett(key: str):
    try:
        roulette = desktop.window(class_name="GlassWndClass-GlassWindowClass-2")
        notepad = desktop.window(class_name="Notepad")
        roulette.set_focus()
        # notepad.set_focus()
        send_keys(key)

    except Exception as e:
        print(e)

def knecht():
    for window in desktop.windows():
        print(window.window_text(), dir(window))
    active_window_handle = ctypes.windll.user32.GetForegroundWindow()

    # Use pywinauto to get the window object
    active_window = Desktop(backend="uia").window(handle=active_window_handle)

    # Print the title of the active window
    print("Currently focused window title:", active_window.window_text())


def scroll():
    try:
        pdf = desktop.window(class_name="AcrobatSDIWindow")
        pdf.set_focus()
        pdf_rect = pdf.rectangle()
        coords = (int((pdf_rect.left + pdf_rect.right) / 2), int((pdf_rect.top + pdf_rect.bottom) / 2))
        print(coords)
        pywinauto.mouse.click(button="left", coords=coords)
        pywinauto.mouse.scroll(coords=coords, wheel_dist=10)
        time.sleep(5)
        pdf.wheel_mouse_input(wheel_dist=100)
        time.sleep(5)
        send_keys("%{TAB}")
        wheel_mouse_input(wheel_dist=100)
    except Exception as e:
        print(e)
        print("Kein PDF mit Acrobat geöffnet")


desktop = Desktop(backend="uia")
# spinRouelett("{- down}"
#              "{- up}")
knecht()