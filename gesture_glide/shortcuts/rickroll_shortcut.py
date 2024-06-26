# Autoren: Isabel Barbu,Nick Büttner,Luke Grasser
import pywhatkit
import logging

from gesture_glide.shortcuts.application_shortcut import ApplicationShortcut


# Defining a class that inherits from ApplicationShortcut
class RickRollShortcut(ApplicationShortcut):
    """Opening Rick Roll with autoplay through recognized hand gesture"""

    # Method to execute the Rick Roll
    def execute(self):
        try:
            # Using pywhatkit to play the Rick Roll video on YouTube
            pywhatkit.playonyt("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
            print("You're getting Rick'n'Rolled!!")  # Print message to indicate Rick Roll
        except Exception as e:
            logging.error(e)  # Log any exceptions that occur
