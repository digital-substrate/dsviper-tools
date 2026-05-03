from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame
from dsviper import BlobGetting, ValueBlobId

from .ui_ds_blobs import Ui_DSBlobs
from .ds_blobs_tree_view_item import DSBlobsTreeWidgetItem

from .ds_helper import byte_count

class DSBlobs(QFrame, Ui_DSBlobs):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)

        self._blobIds: set[ValueBlobId] = set()

        self._blob_getting: BlobGetting | None = None
        self._setup_connections()

    def set_blob_getting(self, blob_getting: BlobGetting):
        self._blob_getting = blob_getting
        self.w_tree_widget.sortItems(0, Qt.SortOrder.AscendingOrder)
        self._setup_blob_infos()
        self._configure_statistics()
        self.w_refresh_button.setEnabled(True)

    def unset_blob_getting(self):
        self._blob_getting = None
        self._clear()

    def _refresh_clicked(self):
        self._configure()

    def _setup_connections(self):
        self.w_tree_widget.setMinimumWidth(730)
        self.w_tree_widget.setColumnWidth(0, 350)
        self.w_tree_widget.setColumnWidth(1, 70)
        self.w_tree_widget.setColumnWidth(2, 120)
        self.w_tree_widget.setColumnWidth(3, 70)

        self.w_refresh_button.clicked.connect(self._refresh_clicked)
        self.w_refresh_button.setEnabled(False)

    def _setup_blob_infos(self):
        self._blobIds = self._blob_getting.blob_ids()
        for info in self._blob_getting.blob_infos(self._blobIds):
            DSBlobsTreeWidgetItem(info, self.w_tree_widget)

        self._sort_blob_infos()

    def _update_blob_infos(self):
        if self._blob_getting.blob_statistics().count() == len(self._blobIds):
            return

        db_blob_ids = self._blob_getting.blob_ids()
        added_blob_ids = db_blob_ids.difference(self._blobIds)
        for info in self._blob_getting.blob_infos(added_blob_ids):
            DSBlobsTreeWidgetItem(info, self.w_tree_widget)

        self._blobIds = db_blob_ids
        self._sort_blob_infos()

    def _sort_blob_infos(self):
        self.w_tree_widget.sortItems(self.w_tree_widget.sortColumn(),
                                     self.w_tree_widget.header().sortIndicatorOrder())

    def _clear(self):
        self._blobIds.clear()
        self.w_count_label.setText("-")
        self.w_total_label.setText("-")
        self.w_min_label.setText("-")
        self.w_max_label.setText("-")
        self.w_tree_widget.clear()
        self.w_refresh_button.setEnabled(False)

    def _configure(self):
        self._configure_statistics()
        self._update_blob_infos()

    def _configure_statistics(self):
        statistics = self._blob_getting.blob_statistics()
        self.w_count_label.setText(str(statistics.count()))
        self.w_total_label.setText(byte_count(statistics.total_size()))
        self.w_min_label.setText(byte_count(statistics.min_size()))
        self.w_max_label.setText(byte_count(statistics.max_size()))
