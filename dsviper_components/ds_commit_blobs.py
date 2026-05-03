from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame

from .ui_ds_commit_blobs import Ui_DSCommitBlobs
from .ds_blobs_tree_view_item import DSBlobsTreeWidgetItem

from dsviper import CommitStore
from .ds_commit_store_notifier import DSCommitStoreNotifier
from .ds_helper import byte_count

class DSCommitBlobs(QFrame, Ui_DSCommitBlobs):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)

        self._store: CommitStore | None = None
        self._setup_connections()

    def set_store(self, store: CommitStore):
        self._store = store

    def _setup_connections(self):
        notifier = DSCommitStoreNotifier.instance()
        notifier.database_did_open.connect(self._store_database_did_open)
        notifier.database_did_close.connect(self._store_database_did_close)
        notifier.state_did_change.connect(self._store_state_did_change)

        self.w_tree_widget.setMinimumWidth(730)
        self.w_tree_widget.setColumnWidth(0, 350)
        self.w_tree_widget.setColumnWidth(1, 70)
        self.w_tree_widget.setColumnWidth(2, 120)
        self.w_tree_widget.setColumnWidth(3, 70)

    def _store_database_did_open(self):
        self.w_tree_widget.sortItems(0, Qt.SortOrder.AscendingOrder)
        self._setup_blob_infos()

    def _store_database_did_close(self):
        self._clear()

    def _store_state_did_change(self):
        self._configure()

    def _setup_blob_infos(self):
        database = self._store.database()
        self._blobIds = database.blob_ids()
        for info in database.commit_databasing().blob_infos(self._blobIds):
            DSBlobsTreeWidgetItem(info, self.w_tree_widget)

        self._sort_blob_infos()

    def _update_blob_infos(self):
        database = self._store.database()
        if database.blob_statistics().count() == len(self._blobIds):
            return

        db_blob_ids = database.blob_ids()
        added_blob_ids = db_blob_ids.difference(self._blobIds)
        for info in database.commit_databasing().blob_infos(added_blob_ids):
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

    def _configure(self):
        self._configure_statistics()
        self._update_blob_infos()

    def _configure_statistics(self):
        database = self._store.database()
        statistics = database.blob_statistics()
        self.w_count_label.setText(str(statistics.count()))
        self.w_total_label.setText(byte_count(statistics.total_size()))
        self.w_min_label.setText(byte_count(statistics.min_size()))
        self.w_max_label.setText(byte_count(statistics.max_size()))
