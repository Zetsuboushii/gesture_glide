import enum
from typing import List, Dict

import yaml


class ShortcutType(enum.StrEnum):
    ROULETTE = "roulette"


class ApplicationShortcutConfig:
    shortcut: ShortcutType
    class_name: str

    def __init__(self, data: Dict[str, str]):
        self.shortcut = ShortcutType(data["shortcut"])
        self.class_name = data["class_name"]



class Config:
    application_shortcuts: List[ApplicationShortcutConfig]

    def __init__(self, data: Dict[str, list[ApplicationShortcutConfig]]):
        self.application_shortcuts = list(map(lambda shortcut: ApplicationShortcutConfig(shortcut), data.get("shortcuts", [])))


def load_config() -> Config:
    data = yaml.safe_load(open("gesture_glide_config.yml"))
    return Config(data)
