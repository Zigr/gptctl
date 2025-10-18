from datetime import datetime
from enum import Enum
from typing import Any


class Conversation:
    def __init__(
        self, title: str, created: datetime | str, count: int, conversation: dict = {}
    ):
        self.title: str = title
        self.created: datetime | str = created
        self.count: int = count
        self.conversation: dict = conversation

    def get(self, key: str, default: Any = "Not found"):
        try:
            attr = getattr(self, key)
        except AttributeError:
            attr = self.conversation.get(key, default)
        return attr

    def __getitem__(self, key: str):
        return getattr(self, key, f"{key} not found")

    def __repr__(self):
        return f"Conversation(title={self.title}, created={self.created}, count={self.count})"

    # Convert the object to a dictionary
    def to_dict(self) -> dict[Any, Any]:
        return self.conversation


class SortFields(str, Enum):
    NO_SORT = "no_sort"
    TITLE = "title"
    CREATED = "created"
    COUNT = "count"


class SortOrder(str, Enum):
    ASC = "asc"
    DESC = "desc"