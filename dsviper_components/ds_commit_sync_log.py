from __future__ import annotations

from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QFrame, QTextEdit

from .ui_ds_commit_sync_log import Ui_DSCommitSyncLog


class DSCommitSyncLog(QFrame, Ui_DSCommitSyncLog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)
        self.w_clear_button.clicked.connect(self._clear_clicked)

    def print_message(self, level: int, message: str):
        self._fast_append(message, self.w_text_edit)

    def clear(self):
        self.w_text_edit.clear()

    def _clear_clicked(self):
        self.clear()

    def _fast_append(self, message: str, widget: QTextEdit):
        at_bottom = widget.verticalScrollBar().value() == widget.verticalScrollBar().maximum()
        doc = widget.document()
        cursor = QTextCursor(doc)
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.beginEditBlock()
        cursor.insertBlock()
        cursor.insertHtml(message)
        cursor.endEditBlock()

        if at_bottom:
            self._scroll_log_to_bottom(widget)

    def _scroll_log_to_bottom(self, widget: QTextEdit):
        bar = widget.verticalScrollBar()
        bar.setValue(bar.maximum())
