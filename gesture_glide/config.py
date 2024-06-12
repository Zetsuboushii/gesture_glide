# Autoren: Miguel Themann
import enum
from typing import List, Dict

import yaml


class ShortcutType(enum.StrEnum):
    OPEN = "open"


class Mode(enum.StrEnum):
    SCROLL = "scroll"
    ROULETTE = "roulette"


class ApplicationShortcutConfig:
    type: ShortcutType
    class_name: str
    mode: Mode

    def __init__(self, data: Dict[str, str]):
        self.type = ShortcutType(data["type"])
        self.class_name = data["class_name"]
        self.mode = Mode(data["mode"])


class Config:
    application_shortcuts: List[ApplicationShortcutConfig]
    scroll_distance_threshold: float

    def __init__(self, data: Dict[str, list[ApplicationShortcutConfig] | float]):
        self.application_shortcuts = list(
            map(lambda shortcut: ApplicationShortcutConfig(shortcut), data.get("shortcuts", [])))
        self.scroll_distance_threshold = data["scroll_distance_threshold"]


def load_config() -> Config:
    data = yaml.safe_load(open("gesture_glide.config.yml"))
    return Config(data)
