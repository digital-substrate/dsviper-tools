from __future__ import annotations

from PySide6.QtCore import QObject, Signal


class DSLogger(QObject):
    messageReceived = Signal(int, str)

    def __init__(self, level: int, *args, **kwarg):
        super().__init__(*args, **kwarg)
        self._level = level

    def log(self, level: int, message: str):
        self.messageReceived.emit(level, message)
