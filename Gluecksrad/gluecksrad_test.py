from pywinauto import Desktop
from pywinauto.keyboard import send_keys
import pywinauto.mouse
import time

def spinRouelett():
    try:
        roulette = desktop.window(class_name="GlassWndClass-GlassWindowClass-2")
        roulette.set_focus()
        send_keys("{SPACE}")
        time.sleep(20)
        send_keys("%{TAB}")
    except:
        print("Glücksrad ist nicht offen, bitte öffne es und probiere es erneut")

def scroll():
    try:
        pdf = desktop.window(class_name="AcrobatSDIWindow")
        pdf.set_focus()
        pdf_rect = pdf.rectangle()
        coords = (int((pdf_rect.left + pdf_rect.right)/2),int((pdf_rect.top + pdf_rect.bottom)/2))
        print(coords)
        pywinauto.mouse.click(button="left",coords=coords)
        pywinauto.mouse.scroll(coords=coords, wheel_dist=10)
        time.sleep(5)
        pdf.wheel_mouse_input(wheel_dist=100)
        time.sleep(5)
        send_keys("%{TAB}")
    except Exception as e:
        print(e)
        print("Kein PDF mit Acrobat geöffnet")

desktop = Desktop(backend="uia")
scroll()