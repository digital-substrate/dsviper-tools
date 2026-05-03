from __future__ import annotations

from PySide6.QtWidgets import QTreeWidgetItem
from dsviper import BlobInfo
from .ds_helper import byte_count

class DSBlobsTreeWidgetItem(QTreeWidgetItem):
    def __init__(self, blob_info: BlobInfo, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._blob_id = blob_info.blob_id()
        self._blob_layout = blob_info.blob_layout()
        self._size = blob_info.size()
        self._chunked = blob_info.chunked()
        self._row_id = blob_info.row_id()

        self.setText(0, self._blob_id.representation())
        self.setText(1, self._blob_layout.representation())
        self.setText(2, byte_count(self._size))
        self.setText(3, "Yes" if self._chunked else "No")
        self.setText(4, str(self._row_id))

    def __lt__(self, other: DSBlobsTreeWidgetItem):
        match self.treeWidget().sortColumn():
            case 1:
                return self._blob_layout < other._blob_layout
            case 2:
                return self._size < other._size
            case 3:
                return self._chunked < other._chunked
            case 4:
                return self._row_id < other._row_id
            case _:
                return self._blob_id < other._blob_id
