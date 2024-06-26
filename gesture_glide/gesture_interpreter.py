# Autoren: Isabel Barbu,Nick Büttner,Miguel Themann,Luke Grasser
import time
from gesture_glide.config import Config
from gesture_glide.gesture_recognizer import GestureRecognizer
from gesture_glide.hand_movement_recognizer import HandMovementRecognizer
from gesture_glide.mp_wrapper import MPWrapper
from gesture_glide.shortcuts.generic_scroll_shortcut import GenericScrollShortcut
from gesture_glide.shortcuts.rickroll_shortcut import RickRollShortcut
from gesture_glide.shortcuts.roulette_command_shortcut import RouletteCommandShortcut
from gesture_glide.shortcuts.roulette_open_shortcut import RouletteOpenShortcut
from gesture_glide.shortcuts.microsoft_office_powerpoint_shortcut import MicrosoftOfficePowerPointCommandShortcut
from gesture_glide.utils import Observer, RecognizedGesture, GestureMode, Observable


class GestureInterpreter(Observer, Observable):
    """Handles interpretation of already detected `RecognizedGesture`s"""
    config: Config

    # Initializing the GestureInterpreter class
    def __init__(self, config: Config, mp_wrapper: MPWrapper, movement_recognizer: HandMovementRecognizer,
                 gesture_recognizer: GestureRecognizer):
        super().__init__()  # Initialize the parent classes
        self.config = config  # Storing configuration
        mp_wrapper.add_observer(self)  # Adding self as an observer to mp_wrapper
        movement_recognizer.add_observer(self)  # Adding self as an observer to movement_recognizer
        gesture_recognizer.add_observer(self)  # Adding self as an observer to gesture_recognizer
        self.gesture_mode = GestureMode.DEFAULT  # Setting initial gesture mode
        self.scroll_shortcut = GenericScrollShortcut(config)  # Initializing scroll shortcut
        self.roulette_open_shortcut = RouletteOpenShortcut(config)  # Initializing roulette open shortcut
        self.roulette_command_shortcut = RouletteCommandShortcut(config)  # Initializing roulette command shortcut
        self.rickroll_shortcut = RickRollShortcut(config)  # Initializing Rick Roll shortcut
        self.microsoft_office_powerpoint_shortcut = MicrosoftOfficePowerPointCommandShortcut(
            config)  # Initializing PowerPoint shortcut
        self.last_gesture_time = 0  # Initializing last gesture time

    # Method to start the scroll shortcut
    def run(self):
        self.scroll_shortcut.run()

    # Method to stop the scroll shortcut
    def stop(self):
        self.scroll_shortcut.stop()

    # Method to update based on observed events
    def update(self, observable, *args, **kwargs):
        scroll_command = kwargs.get("scroll_command")  # Getting scroll command from kwargs
        gesture = kwargs.get("recognized_gesture")  # Getting recognized gesture from kwargs
        time_delta = time.time() - self.last_gesture_time  # Calculating time difference since last gesture

        # Ignore scroll commands if immediately after gesture (e.g., when switching between thumbs up/down relatively
        # quickly)
        if scroll_command is not None and time_delta > 1:
            self.process_scroll_command(**kwargs)
        elif gesture:
            if self.should_process_new_gesture(gesture):
                self.process_gesture(gesture)
        self.notify_observers(gesture_mode=self.gesture_mode)  # Notify observers of the gesture mode

    # Method to apply user settings for scroll speed
    def apply_user_settings(self, scroll_speed_multiplier: float):
        self.scroll_shortcut.apply_user_settings(scroll_speed_multiplier)

    # Method to determine if a new gesture should be processed based on a cooldown period
    def should_process_new_gesture(self, gesture: RecognizedGesture | None) -> bool:
        """Determine if gesture should be processed based on their cooldown period to prevent multiple
        activations over multiple frames in a short interval."""
        current_time = time.time()  # Getting current time
        time_diff = current_time - self.last_gesture_time  # Calculating time difference since last gesture
        if GestureMode.DEFAULT:  # If in default mode
            if time_diff < 5:
                return False  # Ignore if time difference is less than 5 seconds
        else:
            if gesture == RecognizedGesture.OPEN_ROULETTE and time_diff < 5:
                return False  # Ignore if opening roulette and time difference is less than 5 seconds
            if time_diff < 1:
                return False  # Ignore if time difference is less than 1 second
        self.last_gesture_time = current_time  # Update last gesture time
        return True

    # Method to process scroll commands
    def process_scroll_command(self, **kwargs):
        if self.gesture_mode is GestureMode.ROULETTE:  # If in roulette mode
            self.roulette_command_shortcut.execute("SPACE")  # Execute roulette command shortcut with SPACE
        else:
            self.scroll_shortcut.execute(**kwargs)  # Execute scroll shortcut with provided arguments

    # Method to process gestures
    def process_gesture(self, gesture):
        match self.gesture_mode:
            case GestureMode.DEFAULT:
                self.process_default_mode_gesture(gesture)  # Process gesture in default mode
            case GestureMode.ROULETTE:
                self.process_roulette_mode_gesture(gesture)  # Process gesture in roulette mode

    # Method to process gestures in default mode
    def process_default_mode_gesture(self, gesture):
        match gesture:
            case RecognizedGesture.OPEN_ROULETTE:
                self.roulette_open_shortcut.execute()  # Execute roulette open shortcut
                self.gesture_mode = GestureMode.ROULETTE  # Change gesture mode to roulette
            case RecognizedGesture.RICK_ROLL:
                self.rickroll_shortcut.execute()  # Execute Rick Roll shortcut

    # Method to process gestures in roulette mode
    def process_roulette_mode_gesture(self, gesture):
        match gesture:
            case RecognizedGesture.ROULETTE_PLUS:
                self.microsoft_office_powerpoint_shortcut.execute("LEFT")  # Execute PowerPoint shortcut with LEFT key
                self.roulette_command_shortcut.execute("+")  # Execute roulette command shortcut with +
            case RecognizedGesture.ROULETTE_MINUS:
                self.microsoft_office_powerpoint_shortcut.execute("RIGHT")  # Execute PowerPoint shortcut with RIGHT key
                self.roulette_command_shortcut.execute("-")  # Execute roulette command shortcut with -
            case RecognizedGesture.OPEN_ROULETTE:
                self.roulette_open_shortcut.switch_to_previous_screen()  # Switch to the previous screen
                self.gesture_mode = GestureMode.DEFAULT  # Change gesture mode to default
