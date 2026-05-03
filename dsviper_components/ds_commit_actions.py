from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QGuiApplication, QIcon
from PySide6.QtWidgets import QFrame, QListWidgetItem

from .ds_commit_store_notifier import DSCommitStoreNotifier
from .ui_ds_commit_actions import Ui_DSCommitActions
from dsviper import CommitStore

class DSCommitActions(QFrame, Ui_DSCommitActions):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)
        self._store: CommitStore | None = None

        self._setup_connections()

        dark = "-dark" if QGuiApplication.styleHints().colorScheme() == Qt.ColorScheme.Dark else ""
        self._eye_icon = QIcon(f':/dsviper_components/images/eye{dark}')
        self._eye_slash_icon = QIcon(f':/dsviper_components/images/eye.slash{dark}')

    def set_store(self, store: CommitStore):
        self._store = store

    def _setup_connections(self):
        notifier = DSCommitStoreNotifier.instance()
        notifier.database_did_open.connect(self._store_database_did_open)
        notifier.database_did_close.connect(self._store_database_did_close)
        notifier.state_did_change.connect(self._store_state_did_change)
        self.w_list_widget.itemDoubleClicked.connect(self._item_double_clicked)

    def _store_database_did_open(self):
        self.setEnabled(True)
        self.w_list_widget.clear()

    def _store_database_did_close(self):
        self.setEnabled(False)
        self.w_list_widget.clear()

    def _store_state_did_change(self):
        self._configure()

    def _item_double_clicked(self, item: QListWidgetItem):
        if not self._store.has_database():
            return

        index = self.w_list_widget.indexFromItem(item)
        row = index.row()
        eval_action = self._store.state().eval_actions()[row]
        self._store.dispatch_enable_commit(eval_action.header().commit_id(), not eval_action.enabled())

    def _configure(self):
        self.w_list_widget.clear()
        if not self._store.has_database():
            return

        for eval_action in self._store.state().eval_actions()[:-1]:
            icon = self._eye_icon if eval_action.enabled() else self._eye_slash_icon
            item = QListWidgetItem(icon, eval_action.header().label())
            self.w_list_widget.addItem(item)
