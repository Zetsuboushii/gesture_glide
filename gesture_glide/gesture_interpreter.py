import enum

from gesture_glide.config import Config
from gesture_glide.gesture_recognizer import GestureRecognizer
from gesture_glide.mp_wrapper import MPWrapper
from gesture_glide.hand_movement_recognizer import HandMovementRecognizer
from gesture_glide.shortcuts.generic_scroll_shortcut import GenericScrollShortcut
from gesture_glide.shortcuts.roulette_open_shortcut import RouletteOpenShortcut
from gesture_glide.shortcuts.roulette_command_shortcut import RouletteCommandShortcut
from gesture_glide.utils import Observer, FrameData, HandMovementState, HandMovementType, RecognizedGesture, \
    switch_to_previous_screen


class GestureMode(enum.Enum):
    NONE = 0
    ROULETTE = 1


class GestureInterpreter(Observer):
    config: Config

    def __init__(self, config: Config, mp_wrapper: MPWrapper, movement_recognizer: HandMovementRecognizer,
                 gesture_recognizer: GestureRecognizer):
        self.config = config
        mp_wrapper.add_observer(self)
        movement_recognizer.add_observer(self)
        gesture_recognizer.add_observer(self)
        self.gesture_mode = GestureMode.NONE
        self.scroll_shortcut = GenericScrollShortcut(config)
        self.roulette_open_shortcut = RouletteOpenShortcut(config)
        self.roulette_command_shortcut = RouletteCommandShortcut(config)

    def run(self):
        self.scroll_shortcut.run()

    def stop(self):
        self.scroll_shortcut.stop()

    def update(self, observable, *args, **kwargs):
        scroll_command = kwargs.get("scroll_command")
        gesture = kwargs.get("recognized_gesture")
        match self.gesture_mode:
            case GestureMode.NONE:
                if scroll_command is not None:
                    self.scroll_shortcut.execute(**kwargs)
                elif gesture:
                    match gesture:
                        case RecognizedGesture.OPEN_ROULETTE:
                            self.roulette_open_shortcut.execute()
                            self.gesture_mode = GestureMode.ROULETTE
            case GestureMode.ROULETTE:
                if scroll_command is not None:
                    self.roulette_command_shortcut.execute("SPACE")
                else:
                    match gesture:
                        case RecognizedGesture.ROULETTE_PLUS:
                            self.roulette_command_shortcut.execute("+")
                        case RecognizedGesture.ROULETTE_MINUS:
                            self.roulette_command_shortcut.execute("-")
                        case RecognizedGesture.OPEN_ROULETTE:
                            switch_to_previous_screen()
                            self.gesture_mode = GestureMode.NONE