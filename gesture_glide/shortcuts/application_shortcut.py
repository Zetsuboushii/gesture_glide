from gesture_glide.config import Config


class ApplicationShortcut:
    config: Config

    def __init__(self, config: Config):
        self.config = config

    def execute(self):
        raise NotImplementedError()
