from __future__ import annotations

from enum import Enum

class DSCommitSynchronizationSource(Enum):
    NONE = 0
    FILE = 1
    SOCKET = 2
    HOST = 3

