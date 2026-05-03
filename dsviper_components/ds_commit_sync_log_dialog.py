from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QDialog, QHBoxLayout

from .ds_commit_sync_log import DSCommitSyncLog


class DSCommitSyncLogDialog(QDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._commit_sync_log = DSCommitSyncLog()

        layout = QHBoxLayout(self)
        layout.addWidget(self._commit_sync_log)
        self.setLayout(layout)

        self.setWindowIcon(QIcon(":/dsviper_components/images/app.png"))
        self.setWindowTitle("Sync Logger")

    def print_message(self, level: int, message: str):
        self._commit_sync_log.print_message(level, message)
