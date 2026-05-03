from __future__ import annotations

from PySide6.QtCore import QTimer, QDateTime
from PySide6.QtWidgets import QFrame, QLabel
from PySide6.QtGui import QGuiApplication

from .ds_commit_store_notifier import DSCommitStoreNotifier
from .ds_commits_view import DSCommitsView
from .ui_ds_commits import Ui_DSCommits

from dsviper import CommitStore, ValueCommitId, ViperError

class DSCommits(QFrame, Ui_DSCommits):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)

        self._store: CommitStore | None = None
        self._timer = QTimer(self)
        self._commits_view: DSCommitsView | None = None

        self._set_all_buttons_enabled(False)
        self._setup_connections()

    def set_store(self, store: CommitStore):
        self._store = store

        self._commits_view = DSCommitsView(store)
        self._commits_view.selection_changed.connect(self._commits_view_selection_changed)
        self._commits_view.mark_selection_changed.connect(self._commits_view_marked_selection_changed)

        self.scrollarea.setWidget(self._commits_view)

    def _setup_connections(self):
        notifier = DSCommitStoreNotifier.instance()

        notifier.database_did_open.connect(self._store_database_did_open)
        notifier.database_did_close.connect(self._store_database_did_close)
        notifier.state_did_change.connect(self._store_state_did_change)

        #  Commit Actions
        self.w_reset_button.clicked.connect(self._reset_commits_clicked)
        self.w_delete_button.clicked.connect(self._delete_clicked)
        self.w_enable_button.clicked.connect(self._enable_clicked)
        self.w_disable_button.clicked.connect(self._disable_clicked)
        self.w_merge_button.clicked.connect(self._merge_clicked)

        #  Copy Identifiers
        self.w_current_id_button.clicked.connect(self._current_id_copy_clicked)
        self.w_current_parent_id_button.clicked.connect(self._current_parent_id_copy_clicked)
        self.w_current_target_id_button.clicked.connect(self._current_target_id_copy_clicked)

        self.w_marked_id_button.clicked.connect(self._marked_id_copy_clicked)
        self.w_marked_parent_id_button.clicked.connect(self._marked_parent_id_copy_clicked)
        self.w_marked_target_id_button.clicked.connect(self._marked_target_id_copy_clicked)

        self._timer.timeout.connect(self._timer_timeout)

    def _store_database_did_open(self):
        self._set_all_buttons_enabled(True)
        self._clear_current_commit()
        self._clear_marked_commit()
        self._configure()

        self._timer.start(1000)

    def _store_database_did_close(self):
        self._timer.stop()
        self._set_all_buttons_enabled(False)
        self._clear_current_commit()
        self._clear_marked_commit()
        self._commits_view.update_store()

    def _store_state_did_change(self):
        self._configure()

    def _current_id_copy_clicked(self):
        self._copy_identifier(self.w_current_id_label)

    def _current_parent_id_copy_clicked(self):
        self._copy_identifier(self.w_current_parent_id_label)

    def _current_target_id_copy_clicked(self):
        self._copy_identifier(self.w_current_target_id_label)

    def _marked_id_copy_clicked(self):
        self._copy_identifier(self.w_marked_id_label)

    def _marked_parent_id_copy_clicked(self):
        self._copy_identifier(self.w_marked_parent_id_label)

    def _marked_target_id_copy_clicked(self):
        self._copy_identifier(self.w_marked_target_id_label)

    def _delete_clicked(self):
        try:
            if not self._store.has_database():
                return
            self._store.delete_commit(self._store.state().commit_id())

        except ViperError as e:
            self._except_present(e)

    def _reset_commits_clicked(self):
        self._store.notify_reset_database()

    def _enable_clicked(self):
        if not self._store.has_database():
            return
        if self._commits_view.marked_commit_id is None:
            return

        try:
            enabled_commit_id = self._commits_view.marked_commit_id
            self._commits_view.marked_commit_id = None
            self._store.enable_commit(enabled_commit_id)
            self._commits_view.update_graph(False, self.scrollarea)

        except ViperError as e:
            self._except_present(e)

    def _disable_clicked(self):
        if not self._store.has_database():
            return
        if self._commits_view.marked_commit_id is None:
            return

        try:
            disabled_commit_id = self._commits_view.marked_commit_id
            self._commits_view.marked_commit_id = None
            self._store.disable_commit(disabled_commit_id)
            self._commits_view.update_graph(False, self.scrollarea)

        except ViperError as e:
            self._except_present(e)

    def _merge_clicked(self):
        if self._commits_view.marked_commit_id is None:
            return

        try:
            merge_commit_id = self._commits_view.marked_commit_id
            self._commits_view.marked_commit_id = None
            self._store.merge_commit(merge_commit_id)

        except ViperError as e:
            self._except_present(e)

    def _commits_view_marked_selection_changed(self, commit_id: ValueCommitId):
        if self._commits_view.marked_commit_id and self._commits_view.marked_commit_id == commit_id:
            self._commits_view.marked_commit_id = None
            self._configure_marked_commit()
            self._set_marked_buttons_enable(False)
            self._commits_view.update_graph(False, self.scrollarea)
            return

        self._commits_view.marked_commit_id = commit_id
        self._configure_marked_commit()
        self._configure_marked_buttons()

    def _commits_view_selection_changed(self, commit_id: ValueCommitId):
        self._store.notify_stop_live()

        if not self._store.has_database():
            return

        try:
            if commit_id == self._store.state().commit_id():
                return

            self._store.use_commit(commit_id)
            self._store.reset_undo_redo()
            self._store.notify_state_did_change()

        except ViperError as e:
            self._except_present(e)

    def _timer_timeout(self):
        self._commits_view.update_store()

    def _repr_commit_id(self, commit_id: ValueCommitId):
        return commit_id.encoded() if commit_id.is_valid() else ""

    def _configure(self):
        self._configure_current_commit()
        self._configure_marked_commit()

        self._commits_view.current_commit_id = None
        if not self._store.has_database():
            return

        self._configure_marked_buttons()
        self._configure_reset_button()
        self._configure_delete_button()
        self._commits_view.update_store()

    def _configure_current_commit(self):
        if not self._store.has_database():
            return

        try:
            commit_id = self._store.state().commit_id()
            if not commit_id.is_valid():
                return

            database = self._store.database()
            header = database.commit_header(commit_id)
            if header is None:
                self._clear_current_commit()
                return

            self.w_current_id_label.setText(self._repr_commit_id(header.commit_id()))
            self.w_current_id_button.setEnabled(True)

            self.w_current_parent_id_label.setText(self._repr_commit_id(header.parent_commit_id()))
            self.w_current_parent_id_button.setEnabled(True)

            self.w_current_type_label.setText(header.commit_type())

            self.w_current_target_id_label.setText(self._repr_commit_id(header.target_commit_id()))
            self.w_current_target_id_button.setEnabled(True)

            self.w_current_label_label.setText(header.label())

            dt = QDateTime.fromSecsSinceEpoch(int(header.timestamp()))
            self.w_current_date_label.setText(dt.toString())

            self._commits_view.update_commit_states(commit_id)
            self._commits_view.update_graph(True, self.scrollarea)

        except ViperError as e:
            self._except_present(e)

    def _clear_current_commit(self):
        na = "-"
        self.w_current_id_label.setText(na)
        self.w_current_id_button.setEnabled(False)

        self.w_current_parent_id_label.setText(na)
        self.w_current_parent_id_button.setEnabled(False)

        self.w_current_type_label.setText(na)

        self.w_current_target_id_label.setText(na)
        self.w_current_target_id_button.setEnabled(False)

        self.w_current_label_label.setText(na)
        self.w_current_date_label.setText(na)

    def _configure_marked_commit(self):
        if not self._store.has_database():
            return

        if self._commits_view.marked_commit_id is None:
            self._clear_marked_commit()
            return

        database = self._store.database()
        has_commit = database.commit_exists(self._commits_view.marked_commit_id)
        if not has_commit:
            self._commits_view.marked_commit_id = None
            self._clear_marked_commit()
            return

        try:
            header = database.commit_header(self._commits_view.marked_commit_id)

            self.w_marked_id_label.setText(self._repr_commit_id(header.commit_id()))
            self.w_marked_id_button.setEnabled(True)

            self.w_marked_parent_id_label.setText(self._repr_commit_id(header.parent_commit_id()))
            self.w_marked_parent_id_button.setEnabled(True)

            self.w_marked_type_label.setText(header.commit_type())

            self.w_marked_target_id_label.setText(self._repr_commit_id(header.target_commit_id()))
            self.w_marked_target_id_button.setEnabled(True)

            self.w_marked_label_label.setText(header.label())

            dt = QDateTime.fromSecsSinceEpoch(int(header.timestamp()))
            self.w_marked_date_label.setText(dt.toString())

            self._commits_view.update_graph(False, self.scrollarea)

        except ViperError as e:
            self._except_present(e)

    def _clear_marked_commit(self):
        na = "-"
        self.w_marked_id_label.setText(na)
        self.w_marked_id_button.setEnabled(False)

        self.w_marked_parent_id_label.setText(na)
        self.w_marked_parent_id_button.setEnabled(False)

        self.w_marked_type_label.setText(na)

        self.w_marked_target_id_label.setText(na)
        self.w_marked_target_id_button.setEnabled(False)

        self.w_marked_label_label.setText(na)
        self.w_marked_date_label.setText(na)

    def _configure_reset_button(self):
        current_commit_id = self._store.state().commit_id()
        self.w_reset_button.setEnabled(current_commit_id.is_valid())

    def _configure_delete_button(self):
        current_commit_id = self._store.state().commit_id
        commit_ids = self._store.database().commit_ids()
        head_ids = self._store.database().head_commit_ids()
        enabled = current_commit_id in head_ids and len(commit_ids) > 1
        self.w_delete_button.setEnabled(enabled)

    def _configure_marked_buttons(self):
        first_commit_id = self._store.database().first_commit_id()
        if self._commits_view.marked_commit_id and (self._commits_view.marked_commit_id == first_commit_id):
            self._set_marked_buttons_enable(False)
            return

        self._set_marked_buttons_enable(self._commits_view.marked_commit_id is not None)

    def _set_all_buttons_enabled(self, enabled: bool):
        self.w_delete_button.setEnabled(enabled)
        self.w_disable_button.setEnabled(enabled)
        self.w_enable_button.setEnabled(enabled)
        self.w_merge_button.setEnabled(enabled)
        self.w_reset_button.setEnabled(enabled)

    def _set_marked_buttons_enable(self, enabled: bool):
        self.w_delete_button.setEnabled(enabled)
        self.w_disable_button.setEnabled(enabled)
        self.w_enable_button.setEnabled(enabled)
        self.w_merge_button.setEnabled(enabled)

        if self._commits_view.marked_commit_id:
            self.w_merge_button.setEnabled(self._store.database().is_mergeable(self._store.state().commit_id(),
                                                                               self._commits_view.marked_commit_id))

    def _copy_identifier(self, label: QLabel):
        QGuiApplication.clipboard().setText(label.text())

    def _except_present(self, e: ViperError):
        print(e)