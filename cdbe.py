#!/usr/bin/env python
from __future__ import annotations

from PySide6.QtCore import QCoreApplication, Qt, QDir, QFileInfo, QTimer, QRect, QKeyCombination, QCommandLineParser
from PySide6.QtGui import QIcon, QAction, QKeySequence, QGuiApplication, QPalette, QColor
from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox, QDialog

from dsviper import (
    CommitSynchronizer,
    CommitStore,
    CommitStoreNotifying,
    CommitDatabase,
    Logging,
    Error,
    ViperError
)
from dsviper import CommitDatabaseSQLite

import resources_rc

from dsviper_components import ds_dialog_helper
from dsviper_components.ds_commit_actions_dialog import DSCommitActionsDialog
from dsviper_components.ds_commit_program_dialog import DSCommitProgramDialog
from dsviper_components.ds_commit_settings_dialog import DSCommitSettingsDialog
from dsviper_components.ds_commit_store_notifier import DSCommitStoreNotifier
from dsviper_components.ds_commit_sync_log_dialog import DSCommitSyncLogDialog
from dsviper_components.ds_commit_blobs_dialog import DSCommitBlobsDialog
from dsviper_components.ds_commit_synchronizer_thread import DSCommitSynchronizerThread
from dsviper_components.ds_commit_undo_dialog import DSCommitUndoDialog
from dsviper_components.ds_commits_dialog import DSCommitsDialog
from dsviper_components.ds_connect_to_server_dialog import DSConnectToServerDialog
from dsviper_components.ds_documents_commit_store import DSDocumentsCommitStore
from dsviper_components.ds_code_editor_dialog import DSCodeEditorDialog
from dsviper_components.ds_inspect_dialog import DSInspectDialog
from dsviper_components.ds_logger import DSLogger
from dsviper_components.ds_settings import DSSettings

from dsviper_components import ds_license
import os
import platform
import sys


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._bootstrap_database_path: str | None = None

        self._live_enabled = False
        self._live_is_manager = False
        self._databases_path = QDir.homePath() + "/Databases"

        self._inspect_dialog: DSInspectDialog | None = None
        self._inspect_dialog_geometry = QRect()

        self._commits_dialog: DSCommitsDialog | None = None
        self._commits_dialog_geometry = QRect()

        self._commit_program_dialog: DSCommitProgramDialog | None = None
        self._commit_program_dialog_geometry = QRect()

        self._commit_undo_dialog: DSCommitUndoDialog | None = None
        self._commit_undo_dialog_geometry = QRect()

        self._commit_actions_dialog: DSCommitActionsDialog | None = None
        self._commit_actions_dialog_geometry = QRect()

        self._commit_sync_log_dialog: DSCommitSyncLogDialog | None = None
        self._commit_sync_log_dialog_geometry = QRect()

        self._commit_blobs_dialog: DSCommitBlobsDialog | None = None
        self._commit_blobs_dialog_geometry = QRect()

        self._code_editor_dialog: DSCodeEditorDialog | None = None
        self._code_editor_dialog_geometry = QRect()

        self._documents: DSDocumentsCommitStore | None = None

        self._synchronizer: CommitSynchronizer | None = None
        self._sync_logger = DSLogger(Logging.LEVEL_ALL)
        self._sync_logging = Logging.create(self._sync_logger)

        self._setup_setting()

        self._setup_central_widget()
        self._setup_dialog()
        self._setup_action()
        self._setup_menu()
        self._setup_toolbar()

        self._setup_connections()
        self._validate_actions()

        self._configure_window_title()
        self._configure_live_manager_action()
        self._configure_go_live_action()

        self.setWindowIcon(QIcon(":/dsviper_components/images/app.png"))
        self.setMinimumSize(800, 600)

        QTimer.singleShot(100, self, self._bootstrap_timeout)

    # Bootstrap
    def set_bootstrap_database_path(self, database_path: str):
        self._bootstrap_database_path = database_path

    def _bootstrap_timeout(self):
        if self._bootstrap_database_path:
            self._set_database(self._bootstrap_database_path)
        else:
            self._may_reopen_last_database()

    def _setup_setting(self):
        QCoreApplication.setOrganizationName("DigitalSubstrate")
        QCoreApplication.setOrganizationDomain("digitalsubstrate.io")
        QCoreApplication.setApplicationName("CDBEditorPy")

        DSSettings().register_default()

    def _setup_dialog(self):
        store = CommitStore.instance()
        self._inspect_dialog = DSInspectDialog()
        self._commits_dialog = DSCommitsDialog(store)
        self._commit_program_dialog = DSCommitProgramDialog(store)
        self._commit_undo_dialog = DSCommitUndoDialog(store)
        self._commit_blobs_dialog = DSCommitBlobsDialog(store)
        self._commit_actions_dialog = DSCommitActionsDialog(store)
        self._commit_sync_log_dialog = DSCommitSyncLogDialog()

        # Python Editor
        from dsviper_components.python_editor_model import PythonEditorModel
        from pathlib import Path
        scripts_folder = str(Path(__file__).parent / "scripts")
        os.makedirs(scripts_folder, exist_ok=True)
        self._python_editor_model = PythonEditorModel(
            scripts_folder,
            namespace_vars={
                "store": store,
                "_documents_panel": self._documents,
            }
        )
        self._code_editor_dialog = DSCodeEditorDialog(self._python_editor_model)
        self._python_editor_model.run_init_script()

    def _setup_action(self):
        dark = "-dark" if QGuiApplication.styleHints().colorScheme() == Qt.ColorScheme.Dark else ""

        # File Actions
        self._open_action = QAction(QIcon.fromTheme(QIcon.ThemeIcon.DocumentOpen), "Open", parent=self)
        self._open_action.setShortcuts(QKeySequence.StandardKey.Open)
        self._open_action.setIconVisibleInMenu(False)
        self._open_action.triggered.connect(self.open_database)

        self._close_action = QAction(self.tr("Close"), parent=self)
        self._close_action.setShortcuts(QKeySequence.StandardKey.Close)
        self._close_action.setIconVisibleInMenu(False)
        self._close_action.triggered.connect(self.close_database)

        self._quit_action = QAction(self.tr("Quit"), parent=self)
        self._quit_action.setShortcuts(QKeySequence.StandardKey.Quit)
        self._quit_action.setIconVisibleInMenu(False)
        self._quit_action.triggered.connect(QCoreApplication.quit, type=Qt.ConnectionType.QueuedConnection)

        self._toggle_inspect_dialog_action = QAction(self.tr("Get Info"), parent=self)
        self._toggle_inspect_dialog_action.setShortcut(
            QKeyCombination(Qt.KeyboardModifier.ControlModifier, Qt.Key.Key_I))
        self._toggle_inspect_dialog_action.triggered.connect(self._toggle_inspect_dialog_triggered)

        self._reopen_last_database_action = QAction(self.tr("Reopen Last Database"), parent=self)
        self._reopen_last_database_action.setCheckable(True)
        self._reopen_last_database_action.triggered.connect(self._reopen_last_database_triggered)

        # Commit Actions
        self._forward_action = QAction(self.tr("Forward"), parent=self)
        self._forward_action.setIcon(QIcon(f':/dsviper_components/images/arrow.up.circle{dark}'))
        self._forward_action.setIconVisibleInMenu(False)
        self._forward_action.triggered.connect(self._forward_triggered)

        self._merge_heads_action = QAction(self.tr("Merge Heads"), parent=self)
        self._merge_heads_action.setIcon(QIcon(f':/dsviper_components/images/arrow.triangle.merge{dark}'))
        self._merge_heads_action.setIconVisibleInMenu(False)
        self._merge_heads_action.triggered.connect(self._merge_heads_triggered)

        self._fetch_action = QAction(self.tr("Fetch"), parent=self)
        self._fetch_action.setIcon(QIcon(f':/dsviper_components/images/icloud.and.arrow.down{dark}'))
        self._fetch_action.setIconVisibleInMenu(False)
        self._fetch_action.triggered.connect(self._fetch_triggered)

        self._push_action = QAction(self.tr("Push"), parent=self)
        self._push_action.setIcon(QIcon(f':/dsviper_components/images/icloud.and.arrow.up{dark}'))
        self._push_action.setIconVisibleInMenu(False)
        self._push_action.triggered.connect(self._push_triggered)

        self._sync_action = QAction(self.tr("Sync"), parent=self)
        self._sync_action.setIcon(QIcon(f':/dsviper_components/images/link.icloud{dark}'))
        self._sync_action.setIconVisibleInMenu(False)
        self._sync_action.triggered.connect(self._sync_triggered)

        # Live Actions
        self._live_manager_action = QAction(self.tr("Manager"), parent=self)
        self._live_manager_action.setIcon(QIcon(f':/dsviper_components/images/person.icloud{dark}'))
        self._live_manager_action.setIconVisibleInMenu(False)
        self._live_manager_action.triggered.connect(self._toggle_live_manager_triggered)

        self._go_live_action = QAction(self.tr("Go Live"), parent=self)
        self._go_live_action.setIcon(QIcon(f':/dsviper_components/images/arrow.triangle.2.circlepath.icloud{dark}'))
        self._go_live_action.setIconVisibleInMenu(False)
        self._go_live_action.triggered.connect(self._toggle_live_triggered)

        # Edit Actions
        self._undo_action = QAction(self.tr("Undo"), parent=self)
        self._undo_action.setShortcut(QKeySequence.StandardKey.Undo)
        self._undo_action.setShortcutContext(Qt.ShortcutContext.ApplicationShortcut)
        self._undo_action.triggered.connect(self._undo_triggered)

        self._redo_action = QAction(self.tr("Redo"), parent=self)
        self._redo_action.setShortcut(QKeySequence.StandardKey.Redo)
        self._redo_action.setShortcutContext(Qt.ShortcutContext.ApplicationShortcut)
        self._redo_action.triggered.connect(self._redo_triggered)

        self._go_forward_action = QAction(self.tr("Go Forward"), parent=self)
        self._go_forward_action.setShortcut(
            QKeyCombination(Qt.KeyboardModifier.ControlModifier | Qt.KeyboardModifier.ShiftModifier, Qt.Key.Key_Right))
        self._go_forward_action.setShortcutContext(Qt.ShortcutContext.ApplicationShortcut)
        self._go_forward_action.triggered.connect(self._go_forward_triggered)

        self._go_back_action = QAction(self.tr("Go Back"), parent=self)
        self._go_back_action.setShortcut(
            QKeyCombination(Qt.KeyboardModifier.ControlModifier | Qt.KeyboardModifier.ShiftModifier, Qt.Key.Key_Left))
        self._go_back_action.setShortcutContext(Qt.ShortcutContext.ApplicationShortcut)
        self._go_back_action.triggered.connect(self._go_back_triggered)

        # Admin Actions
        self._toggle_commits_dialog_action = QAction(self.tr("Commits Panel"), parent=self)
        self._toggle_commits_dialog_action.setShortcut(
            QKeyCombination(Qt.KeyboardModifier.ControlModifier, Qt.Key.Key_1))
        self._toggle_commits_dialog_action.setShortcutContext(Qt.ShortcutContext.ApplicationShortcut)
        self._toggle_commits_dialog_action.triggered.connect(self._toggle_commits_dialog_triggered)

        self._toggle_commit_program_dialog_action = QAction(self.tr("Program Panel"), parent=self)
        self._toggle_commit_program_dialog_action.setShortcut(
            QKeyCombination(Qt.KeyboardModifier.ControlModifier, Qt.Key.Key_3))
        self._toggle_commit_program_dialog_action.setShortcutContext(Qt.ShortcutContext.ApplicationShortcut)
        self._toggle_commit_program_dialog_action.triggered.connect(self._toggle_commit_program_dialog_triggered)

        self._toggle_commit_settings_dialog_action = QAction(self.tr("Commit Settings Panel"), parent=self)
        self._toggle_commit_settings_dialog_action.setShortcut(
            QKeyCombination(Qt.KeyboardModifier.ControlModifier, Qt.Key.Key_4))
        self._toggle_commit_settings_dialog_action.triggered.connect(self._toggle_commit_settings_dialog_triggered)

        self._toggle_commit_undo_dialog_action = QAction(self.tr("Undo Panel"), parent=self)
        self._toggle_commit_undo_dialog_action.setShortcut(
            QKeyCombination(Qt.KeyboardModifier.ControlModifier, Qt.Key.Key_5))
        self._toggle_commit_undo_dialog_action.setShortcutContext(Qt.ShortcutContext.ApplicationShortcut)
        self._toggle_commit_undo_dialog_action.triggered.connect(self._toggle_commit_undo_dialog_triggered)

        self._toggle_commit_sync_log_dialog_action = QAction(self.tr("Synchronizer Log Panel"), self)
        self._toggle_commit_sync_log_dialog_action.setShortcut(
            QKeyCombination(Qt.KeyboardModifier.ControlModifier, Qt.Key.Key_6))
        self._toggle_commit_sync_log_dialog_action.setShortcutContext(Qt.ShortcutContext.ApplicationShortcut)
        self._toggle_commit_sync_log_dialog_action.triggered.connect(self._toggle_commit_sync_log_dialog_triggered)

        self._toggle_commit_blobs_dialog_action = QAction(self.tr("Blobs Panel"), self)
        self._toggle_commit_blobs_dialog_action.setShortcut(
            QKeyCombination(Qt.KeyboardModifier.ControlModifier, Qt.Key.Key_7))
        self._toggle_commit_blobs_dialog_action.setShortcutContext(Qt.ShortcutContext.ApplicationShortcut)
        self._toggle_commit_blobs_dialog_action.triggered.connect(self._toggle_commit_blobs_dialog_triggered)

        self._toggle_commit_actions_dialog_action = QAction(self.tr("Action Panel"), self)
        self._toggle_commit_actions_dialog_action.setShortcut(
            QKeyCombination(Qt.KeyboardModifier.ControlModifier, Qt.Key.Key_8))
        self._toggle_commit_actions_dialog_action.setShortcutContext(Qt.ShortcutContext.ApplicationShortcut)
        self._toggle_commit_actions_dialog_action.triggered.connect(self._toggle_commit_actions_dialog_triggered)

        self._toggle_code_editor_dialog_action = QAction(self.tr("Python &Editor"), parent=self)
        self._toggle_code_editor_dialog_action.setShortcut(
            QKeyCombination(Qt.KeyboardModifier.ControlModifier, Qt.Key.Key_0))
        self._toggle_code_editor_dialog_action.setShortcutContext(Qt.ShortcutContext.ApplicationShortcut)
        self._toggle_code_editor_dialog_action.triggered.connect(self._toggle_code_editor_dialog_triggered)

        self._connect_to_server_action = QAction(self.tr("Connect To Server"), parent=self)
        self._connect_to_server_action.setShortcut(QKeyCombination(Qt.KeyboardModifier.ControlModifier, Qt.Key.Key_K))
        self._connect_to_server_action.triggered.connect(self._connect_to_server_triggered)

        # Help Actions — kept in the Help menu (NoRole) so macOS does not
        # migrate them into the application menu, matching the QML build.
        self._about_action = QAction(self.tr("About CDB Editor..."), parent=self)
        self._about_action.setMenuRole(QAction.MenuRole.NoRole)
        self._about_action.triggered.connect(self._about_triggered)

        self._about_qt_action = QAction(self.tr("About Qt"), parent=self)
        self._about_qt_action.setMenuRole(QAction.MenuRole.NoRole)
        self._about_qt_action.triggered.connect(QApplication.aboutQt)

    def _setup_menu(self):
        file_menu = self.menuBar().addMenu("&File")
        file_menu.addAction(self._open_action)
        file_menu.addAction(self._close_action)
        file_menu.addAction(self._toggle_inspect_dialog_action)
        file_menu.addSeparator()
        file_menu.addAction(self._forward_action)
        file_menu.addAction(self._merge_heads_action)
        file_menu.addSeparator()
        file_menu.addAction(self._fetch_action)
        file_menu.addAction(self._push_action)
        file_menu.addAction(self._sync_action)
        file_menu.addSeparator()
        file_menu.addAction(self._reopen_last_database_action)

        if platform.system() != "Darwin":
            file_menu.addSeparator()
            file_menu.addAction(self._quit_action)

        edit_menu = self.menuBar().addMenu(self.tr("&Edit"))
        edit_menu.addAction(self._undo_action)
        edit_menu.addAction(self._redo_action)

        navigation_menu = self.menuBar().addMenu(self.tr("&Navigation"))
        navigation_menu.addAction(self._go_forward_action)
        navigation_menu.addAction(self._go_back_action)

        # Editor menu
        editor = self._code_editor_dialog.editor
        editor_menu = self.menuBar().addMenu(self.tr("&Editor"))

        editor_menu.addAction(editor.open_script_action)
        editor_menu.addAction(editor.save_script_action)
        editor_menu.addSeparator()

        find_submenu = editor_menu.addMenu(self.tr("Find"))
        find_submenu.addAction(editor.find_action)
        find_submenu.addAction(editor.find_next_action)
        find_submenu.addAction(editor.find_previous_action)
        find_submenu.addAction(editor.use_selection_for_find_action)
        find_submenu.addSeparator()
        find_submenu.addAction(editor.find_and_replace_action)

        editor_menu.addSeparator()
        editor_menu.addAction(editor.next_error_action)
        editor_menu.addAction(editor.previous_error_action)
        editor_menu.addSeparator()
        editor_menu.addAction(editor.jump_to_line_action)
        editor_menu.addAction(editor.jump_to_definition_action)
        editor_menu.addSeparator()
        editor_menu.addAction(editor.run_script_action)
        editor_menu.addAction(editor.eval_selection_action)
        editor_menu.addSeparator()
        editor_menu.addAction(editor.show_help_action)
        editor_menu.addAction(editor.show_type_action)
        editor_menu.addAction(editor.show_description_action)
        editor_menu.addSeparator()
        editor_menu.addAction(editor.bigger_font_action)
        editor_menu.addAction(editor.smaller_font_action)
        editor_menu.addSeparator()
        editor_menu.addAction(editor.comment_selection_action)
        editor_menu.addAction(editor.shift_right_action)
        editor_menu.addAction(editor.shift_left_action)
        editor_menu.addAction(editor.move_line_up_action)
        editor_menu.addAction(editor.move_line_down_action)
        editor_menu.addSeparator()
        editor_menu.addAction(editor.refresh_syntax_action)

        admin_menu = self.menuBar().addMenu(self.tr("&Admin"))
        admin_menu.addAction(self._toggle_commits_dialog_action)
        admin_menu.addAction(self._toggle_commit_program_dialog_action)
        admin_menu.addAction(self._toggle_commit_settings_dialog_action)
        admin_menu.addAction(self._toggle_commit_undo_dialog_action)
        admin_menu.addAction(self._toggle_commit_sync_log_dialog_action)
        admin_menu.addAction(self._toggle_commit_blobs_dialog_action)
        admin_menu.addAction(self._toggle_commit_actions_dialog_action)
        admin_menu.addSeparator()
        admin_menu.addAction(self._toggle_code_editor_dialog_action)
        admin_menu.addSeparator()
        admin_menu.addAction(self._connect_to_server_action)

        help_menu = self.menuBar().addMenu(self.tr("&Help"))
        help_menu.addAction(self._about_action)
        help_menu.addAction(self._about_qt_action)

        settings = DSSettings()
        checked = settings.reopen_last_file
        self._reopen_last_database_action.setChecked(checked)

    def _setup_toolbar(self):
        tb = self.addToolBar(self.tr("ToolBar"))
        tb.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        tb.addAction(self._forward_action)
        tb.addAction(self._merge_heads_action)
        tb.addSeparator()
        tb.addAction(self._fetch_action)
        tb.addAction(self._push_action)
        tb.addAction(self._sync_action)
        tb.addSeparator()
        tb.addAction(self._live_manager_action)
        tb.addAction(self._go_live_action)

    def _setup_central_widget(self):
        self._documents = DSDocumentsCommitStore()
        self._documents.set_store(CommitStore.instance())
        self.setCentralWidget(self._documents)

    def _setup_connections(self):
        notifier = DSCommitStoreNotifier.instance()

        # Database
        notifier.database_did_open.connect(self._store_database_did_open)
        notifier.database_did_close.connect(self._store_database_did_close)
        notifier.state_did_change.connect(self._store_state_did_change)
        notifier.definitions_did_change.connect(self._store_definitions_did_change)

        # Dispatch
        notifier.dispatch_error.connect(self._present_error)

        # Live Mode
        notifier.stop_live.connect(self._store_stop_live)

        # Evil
        notifier.reset_database.connect(self._store_reset_database)
        notifier.database_will_reset.connect(self._store_database_will_reset)

        # Message ?
        self._sync_logger.messageReceived.connect(self._commit_sync_log_dialog.print_message)

    # Slots
    def open_database(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Open Document", self._databases_path, "All files (*.*) ;;")
        if not len(filename):
            return

        self._databases_path = QFileInfo(filename).filePath()
        self._set_database(filename)

    def close_database(self):
        try:
            CommitStore.instance().close()
            self._configure_window_title()
            self._validate_actions()
        except ViperError as e:
            self._except_present(e)

    # Store Notification
    def _store_database_did_open(self):
        self._validate_actions()
        self._inspect_database_did_open()

    def _store_database_did_close(self):
        self._validate_actions()
        self._inspect_database_did_close()

    def _store_reset_database(self):
        CommitStore.instance().reset()

    def _store_database_will_reset(self):
        self._disable_live()

    def _store_definitions_did_change(self):
        self._inspect_definitions_did_change()

    def _store_state_did_change(self):
        store = CommitStore.instance()
        self._undo_action.setEnabled(store.can_undo())
        self._redo_action.setEnabled(store.can_redo())

    def _store_stop_live(self):
        self._disable_live()

    # Actions Slots
    def _reopen_last_database_triggered(self):
        checked = self._reopen_last_database_action.isChecked()
        settings = DSSettings()
        settings.reopen_last_file = checked
        settings.sync()

    def _forward_triggered(self):
        try:
            CommitStore.instance().forward()
        except ViperError as e:
            self._except_present(e)

    def _merge_heads_triggered(self):
        try:
            CommitStore.instance().reduce_heads()
        except ViperError as e:
            self._except_present(e)

    def _fetch_triggered(self):
        self._synchronize(CommitSynchronizer.MODE_FETCH)

    def _push_triggered(self):
        self._synchronize(CommitSynchronizer.MODE_PUSH)

    def _sync_triggered(self):
        self._synchronize(CommitSynchronizer.MODE_SYNC)

    def _toggle_live_manager_triggered(self):
        self._live_is_manager = not self._live_is_manager
        self._configure_live_manager_action()

    def _toggle_live_triggered(self):
        if not self._live_enabled:
            self._enable_live()
        else:
            self._disable_live()

    def _undo_triggered(self):
        CommitStore.instance().undo()

    def _redo_triggered(self):
        CommitStore.instance().redo()

    def _go_forward_triggered(self):
        self._documents.go_forward()

    def _go_back_triggered(self):
        self._documents.go_back()

    def _toggle_inspect_dialog_triggered(self):
        ds_dialog_helper.toggle(self._inspect_dialog, self._inspect_dialog_geometry)

    def _toggle_commits_dialog_triggered(self):
        ds_dialog_helper.toggle(self._commits_dialog, self._commits_dialog_geometry)

    def _toggle_commit_program_dialog_triggered(self):
        ds_dialog_helper.toggle(self._commit_program_dialog, self._commit_program_dialog_geometry)

    def _toggle_commit_settings_dialog_triggered(self):
        DSCommitStoreNotifier.instance().notify_stop_live()
        dialog = DSCommitSettingsDialog(self)
        dialog.exec()
        self._validate_actions()

    def _toggle_commit_undo_dialog_triggered(self):
        ds_dialog_helper.toggle(self._commit_undo_dialog, self._commit_undo_dialog_geometry)

    def _toggle_commit_sync_log_dialog_triggered(self):
        ds_dialog_helper.toggle(self._commit_sync_log_dialog, self._commit_sync_log_dialog_geometry)

    def _toggle_commit_blobs_dialog_triggered(self):
        ds_dialog_helper.toggle(self._commit_blobs_dialog, self._commit_blobs_dialog_geometry)

    def _toggle_commit_actions_dialog_triggered(self):
        ds_dialog_helper.toggle(self._commit_actions_dialog, self._commit_actions_dialog_geometry)

    def _toggle_code_editor_dialog_triggered(self):
        ds_dialog_helper.toggle(self._code_editor_dialog, self._code_editor_dialog_geometry)

    def _connect_to_server_triggered(self):
        dialog = DSConnectToServerDialog(self)
        dialog.exec()
        if dialog.result() == QDialog.DialogCode.Rejected:
            return

        try:
            settings = DSSettings()
            host = settings.connect_hostname
            service = settings.connect_service
            socket_path = settings.connect_socket_path
            use_socket_path = settings.connect_use_socket_path

            if use_socket_path:
                db = CommitDatabase.connect_local(socket_path)
            else:
                db = CommitDatabase.connect(host, service)
            CommitStore.instance().use(db)

        except ViperError as e:
            self._except_present(e)

    def _validate_actions(self):
        store = CommitStore.instance()
        has_database = store.has_database()
        has_sos = DSSettings().has_source_of_synchronization()

        self._open_action.setEnabled(not self._live_enabled)
        self._close_action.setEnabled(not self._live_enabled and has_database)
        self._toggle_inspect_dialog_action.setEnabled(has_database)

        self._forward_action.setEnabled(has_database and not self._live_enabled)
        self._merge_heads_action.setEnabled(has_database and not self._live_enabled)

        self._fetch_action.setEnabled(has_database and has_sos and not self._live_enabled)
        self._push_action.setEnabled(has_database and has_sos and not self._live_enabled)
        self._sync_action.setEnabled(has_database and has_sos and not self._live_enabled)

        self._undo_action.setEnabled(store.can_undo())
        self._redo_action.setEnabled(store.can_redo())

        self._live_manager_action.setEnabled(has_database)
        self._go_live_action.setEnabled(has_database)

    def _configure_window_title(self):
        title = "CDB Editor (PySide)"
        store = CommitStore.instance()

        if store.has_database():
            filename = os.path.basename(store.database().path())
            title = f'{title} - {filename}'

        self.setWindowTitle(title)

    # About
    def _about_triggered(self):
        ds_license.show_about_dialog(self, "CDB Editor", "Commit Database Editor")

    # Inspect
    def _inspect_database_did_open(self):
        inspect = self._inspect_dialog.inspect()
        database = CommitStore.instance().database()
        inspect.set_path(database.path())
        inspect.set_documentation(database.documentation())
        inspect.set_uuid(database.uuid().encoded())
        inspect.set_codec_name(database.codec_name())
        inspect.set_definition_hexdigest(database.definitions_hexdigest())
        inspect.set_definitions(database.definitions())

    def _inspect_database_did_close(self):
        self._inspect_dialog.inspect().clear()

    def _inspect_definitions_did_change(self):
        self._inspect_dialog.inspect().set_definitions(CommitStore.instance().definitions())

    # Live Mode
    def _configure_live_manager_action(self):
        dark = "-dark" if QGuiApplication.styleHints().colorScheme() == Qt.ColorScheme.Dark else ""
        fill = ".fill" if self._live_is_manager else ""
        self._live_manager_action.setIcon(QIcon(f':/dsviper_components/images/person.icloud{fill}{dark}'))

    def _configure_go_live_action(self):
        dark = "-dark" if QGuiApplication.styleHints().colorScheme() == Qt.ColorScheme.Dark else ""
        fill = ".fill" if self._live_enabled else ""
        self._go_live_action.setIcon(QIcon(f':/dsviper_components/images/arrow.triangle.2.circlepath.icloud{fill}{dark}'))

    def _enable_live(self):
        settings = DSSettings()
        live_sync = settings.live_sync_with_source

        try:
            if live_sync:
                path = CommitStore.instance().database().path()
                self._synchronizer = settings.create_synchronizer(CommitSynchronizer.MODE_SYNC, path)

            self._live_enabled = True
            self._configure_go_live_action()
            self._schedule_live_timer()

        except ViperError as e:
            self._except_present(e)

    def _disable_live(self):
        self._synchronizer = None
        self._live_enabled = False
        self._live_is_manager = False

        self._configure_go_live_action()
        self._configure_live_manager_action()

    def _schedule_live_timer(self):
        live_interval = DSSettings().live_update_interval
        interval_ms = (live_interval / 10.0) * 1000.0
        QTimer.singleShot(int(interval_ms), self, self._live_timer_timeout)

    def _live_timer_timeout(self):
        if not self._live_enabled:
            return

        if self._synchronizer:
            thread = DSCommitSynchronizerThread(self._synchronizer, self._sync_logging, self)
            thread.syncDone.connect(self._live_synchronization_done)
            thread.finished.connect(thread.deleteLater)
            thread.start()
        else:
            self._live_schedule_if_safe_reduce_forward()

    def _live_synchronization_done(self, success: bool):
        if not success:
            self._disable_live()
            return

        st: DSCommitSynchronizerThread = self.sender()
        if st.info and st.info.updated_definitions():
            CommitStore.instance().notify_definitions_did_change()

        self._live_schedule_if_safe_reduce_forward()

    def _live_schedule_if_safe_reduce_forward(self):
        if not self._live_safe_reduce_forward():
            self._disable_live()
        else:
            self._schedule_live_timer()

    def _live_safe_reduce_forward(self) -> bool:
        try:
            store = CommitStore.instance()
            if self._live_is_manager:
                store.reduce_heads()
            store.forward()
            return True
        except ViperError:
            return False

    # Database
    def _set_database(self, filename: str):
        try:
            database = CommitDatabase.open(filename)
            CommitStore.instance().use(database)
            self._configure_window_title()
            self._validate_actions()

            settings = DSSettings()
            settings.last_file_url = filename
            settings.sync()
        except ViperError as e:
            self._except_present(e)

    def _may_reopen_last_database(self):
        settings = DSSettings()
        reopen = settings.reopen_last_file
        if not reopen:
            return

        filename = settings.last_file_url
        if not os.path.exists(filename):
            return

        self._set_database(filename)

    def _synchronize(self, mode: str):
        try:
            path = CommitStore.instance().database().path()
            synchronizer = DSSettings().create_synchronizer(mode, path)
            info = synchronizer.sync(self._sync_logging)

            if info.updated_definitions():
                CommitStore.instance().notify_definitions_did_change()

        except ViperError as e:
            self._except_present(e)

    def _except_present(self, e: ViperError):
        self._present_error(Error.parse(str(e)))

    def _present_error(self, error: Error):
        QMessageBox.critical(self, "Error", error.explained(),
                             QMessageBox.StandardButton.Ok,
                             QMessageBox.StandardButton.NoButton)


def main():
    Error.set_process_name("cdbe")

    store = CommitStore.instance()
    notifier = DSCommitStoreNotifier.instance()
    store.set_notifier(CommitStoreNotifying.create(notifier))

    app = QApplication(sys.argv)
    app.setApplicationDisplayName("CDB Editor")
    app.setApplicationName("CDB Editor")
    app.setApplicationVersion(ds_license.VERSION)
    app.setStyle("fusion")
    app.setWindowIcon(QIcon(":/images/cdbe_icon.png"))

    if platform.system() == "Windows":
        if QGuiApplication.styleHints().colorScheme() == Qt.ColorScheme.Dark:
            p = app.palette()
            p.setColor(QPalette.ColorRole.AlternateBase, QColor(60, 60, 60))
            app.setPalette(p)

    # QGuiApplication.styleHints().setColorScheme(Qt.ColorScheme.Light)

    # Parse
    parser = QCommandLineParser()
    parser.addHelpOption()
    parser.addVersionOption()
    parser.addPositionalArgument("database", "Database to open.", "database")
    parser.process(app)
    arguments = parser.positionalArguments()

    database_path: str | None = None

    if len(arguments) > 1:
        parser.showHelp()
        exit(1)

    # Check if the database is present
    elif len(arguments) == 1:
        database_path = arguments[0]
        if not os.path.exists(database_path):
            print(f'No such file {database_path}.')
            exit(1)
        if not CommitDatabaseSQLite.is_compatible(database_path):
            print(f'The SQL schema is not compatible with a Digital Substrate CommitDatabase.')
            exit(1)

    window = MainWindow()
    if database_path:
        window.set_bootstrap_database_path(database_path)

    window.show()
    app.exec()


if __name__ == '__main__':
    main()
