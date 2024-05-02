from pywinauto import Desktop
from pywinauto.keyboard import send_keys
import time

desktop = Desktop(backend="uia")

roulette = desktop.window(class_name="GlassWndClass-GlassWindowClass-2")
roulette.set_focus()
send_keys("{SPACE}")
time.sleep(20)

send_keys("%{TAB}")