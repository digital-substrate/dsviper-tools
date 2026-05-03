from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QComboBox

from .ds_documents_item import DSDocumentsItem


class DSDocumentsComboBoxItem(QComboBox):
    def __init__(self, item: DSDocumentsItem, column: int, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._item = item
        self._column = column
        self.currentIndexChanged.connect(self._change_item)

    def _change_item(self, index: int):
        if index >= 0:
            self._item.setData(self._column, Qt.ItemDataRole.DisplayRole, self.itemText(index))
