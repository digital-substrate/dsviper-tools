from __future__ import annotations

from PySide6.QtCore import QThread, Signal

from dsviper import CommitSynchronizer, CommitSynchronizerInfo, Logging


class DSCommitSynchronizerThread(QThread):
    syncDone = Signal(bool)

    def __init__(self, synchronizer: CommitSynchronizer, logging: Logging, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._synchronizer = synchronizer
        self._logging = logging
        self._info: CommitSynchronizerInfo | None = None

    def run(self):
        try:
            self._info = self._synchronizer.sync(self._logging)
            self.syncDone.emit(True)

        except Exception:
            self.syncDone.emit(False)

    @property
    def info(self) -> CommitSynchronizerInfo | None:
        return self._info
