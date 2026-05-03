from __future__ import annotations

from PySide6.QtWidgets import QStyledItemDelegate


class DSItemDelegateNoEdit(QStyledItemDelegate):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def createEditor(self, parent, option, index):
        return None
