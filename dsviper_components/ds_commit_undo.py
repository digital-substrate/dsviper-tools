from __future__ import annotations

from PySide6.QtWidgets import QFrame, QListWidgetItem

from .ds_commit_store_notifier import DSCommitStoreNotifier
from .ui_ds_commit_undo import Ui_DSCommitUndo
from dsviper import CommitStore, ValueCommitId


class DSCommitUndo(QFrame, Ui_DSCommitUndo):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)
        self._store: CommitStore | None = None
        self._commit_ids: list[ValueCommitId] = []
        self._setup_connections()

    def set_store(self, store: CommitStore):
        self._store = store

    def _setup_connections(self):
        notifier = DSCommitStoreNotifier.instance()
        notifier.database_did_close.connect(self._store_database_did_close)
        notifier.state_did_change.connect(self._store_state_did_change)

    def _store_database_did_close(self):
        self._commit_ids.clear()
        self.w_list_widget.clear()
        pass

    def _store_state_did_change(self):
        self._configure()

    def _configure(self):
        if not self._store.has_database():
            return

        commit_ids, current = self._store.undo_stack_ids()
        commit_ids.reverse()

        if self._commit_ids != commit_ids:
            self._commit_ids = commit_ids

            self.w_list_widget.clear()
            database = self._store.database()
            for commitId in commit_ids:
                header = database.commit_header(commitId)
                item = QListWidgetItem(header.label())
                self.w_list_widget.addItem(item)

        if current:
            row = len(commit_ids) - 1 - current
            self.w_list_widget.setCurrentRow(row)
        else:
            self.w_list_widget.clearSelection()
