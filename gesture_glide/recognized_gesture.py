import enum
from typing import Dict, Any


class GestureType(enum.StrEnum):
    SCROLL = "scroll"
    THUMBS_UP = "thumbs up"


class RecognizedGesture:
    type: GestureType
    data: Dict[Any, Any]

    def __init__(self, type: GestureType, data: Dict[Any, Any]):
        self.type = type
        self.data = data
