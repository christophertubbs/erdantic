"""
Common enums to use within the codebase
"""
from __future__ import annotations

import enum


class Orientation(str, enum.Enum):
    VERTICAL = "TB"
    HORIZONTAL = "LR"

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return f"{self.name} => {self.value}"
