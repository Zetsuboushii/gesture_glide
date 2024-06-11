import time
from gesture_glide.config import Config
from gesture_glide.gesture_recognizer import GestureRecognizer
from gesture_glide.hand_movement_recognizer import HandMovementRecognizer
from gesture_glide.mp_wrapper import MPWrapper
from gesture_glide.shortcuts.generic_scroll_shortcut import GenericScrollShortcut
from gesture_glide.shortcuts.roulette_command_shortcut import RouletteCommandShortcut
from gesture_glide.shortcuts.roulette_open_shortcut import RouletteOpenShortcut
from gesture_glide.utils import Observer, RecognizedGesture, switch_to_previous_screen, GestureMode


class GestureInterpreter(Observer):
    config: Config

    def __init__(self, config: Config, mp_wrapper: MPWrapper, movement_recognizer: HandMovementRecognizer,
                 gesture_recognizer: GestureRecognizer):
        self.config = config
        mp_wrapper.add_observer(self)
        movement_recognizer.add_observer(self)
        gesture_recognizer.add_observer(self)
        self.gesture_mode = GestureMode.DEFAULT
        self.scroll_shortcut = GenericScrollShortcut(config)
        self.roulette_open_shortcut = RouletteOpenShortcut(config)
        self.roulette_command_shortcut = RouletteCommandShortcut(config)
        self.last_gesture_time = 0

    def run(self):
        self.scroll_shortcut.run()

    def stop(self):
        self.scroll_shortcut.stop()

    def update(self, observable, *args, **kwargs):
        scroll_command = kwargs.get("scroll_command")
        gesture = kwargs.get("recognized_gesture")

        if scroll_command is not None:
            self.process_scroll_command(**kwargs)
        elif gesture:
            if not self.should_process_new_gesture():
                return
            self.process_gesture(gesture)

    def should_process_new_gesture(self) -> bool:
        current_time = time.time()
        time_diff = current_time - self.last_gesture_time
        if GestureMode.DEFAULT:
            if time_diff < 5:
                return False
        else:
            if time_diff < 1:
                return False
        self.last_gesture_time = current_time
        return True

    def process_scroll_command(self, **kwargs):
        if self.gesture_mode is GestureMode.ROULETTE:
            self.roulette_command_shortcut.execute("SPACE")
        else:
            self.scroll_shortcut.execute(**kwargs)

    def process_gesture(self, gesture):
        match self.gesture_mode:
            case GestureMode.DEFAULT:
                self.process_default_mode_gesture(gesture)
            case GestureMode.ROULETTE:
                self.process_roulette_mode_gesture(gesture)

    def process_default_mode_gesture(self, gesture):
        match gesture:
            case RecognizedGesture.OPEN_ROULETTE:
                self.roulette_open_shortcut.execute()
                self.gesture_mode = GestureMode.ROULETTE

    def process_roulette_mode_gesture(self, gesture):
        match gesture:
            case RecognizedGesture.ROULETTE_PLUS:
                self.roulette_command_shortcut.execute("+")
            case RecognizedGesture.ROULETTE_MINUS:
                self.roulette_command_shortcut.execute("-")
            case RecognizedGesture.OPEN_ROULETTE:
                switch_to_previous_screen()
                self.gesture_mode = GestureMode.DEFAULT
