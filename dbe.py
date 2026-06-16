#!/usr/bin/env python
from __future__ import annotations

import os
import platform
import sys

from PySide6.QtCore import QCoreApplication, Qt, QDir, QFileInfo, QTimer, QRect, QKeyCombination, QCommandLineParser
from PySide6.QtGui import QIcon, QAction, QKeySequence, QGuiApplication, QPalette, QColor
from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox, QDialog

import resources_rc

from dsviper_components import ds_dialog_helper
from dsviper_components.ds_connect_to_server_dialog import DSConnectToServerDialog
from dsviper_components.ds_documents_databasing import DSDocumentsDatabasing
from dsviper_components.ds_inspect_dialog import DSInspectDialog
from dsviper_components.ds_blobs_dialog import DSBlobsDialog
from dsviper_components.ds_settings import DSSettings
from dsviper_components.ds_database_select_dialog import DSDatabaseSelectDialog

from dsviper_components import ds_license
from _version import __version__
from dsviper import Database, Error, ViperError

class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._bootstrap_database_path: str | None = None
        self._database: Database | None = None

        self._databases_path = QDir.homePath() + "/Databases"

        self._inspect_dialog: DSInspectDialog | None = None
        self._inspect_dialog_geometry = QRect()

        self._blobs_dialog: DSBlobsDialog | None = None
        self._blobs_dialog_geometry = QRect()

        self._setup_setting()
        self._setup_central_widget()
        self._setup_dialog()
        self._setup_action()
        self._setup_menu()
        self._validate_actions()

        self._configure_window_title()

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
        QCoreApplication.setApplicationName("DBEditorPy")

        DSSettings().register_default()

    def _setup_dialog(self):
        self._inspect_dialog = DSInspectDialog()
        self._blobs_dialog = DSBlobsDialog()

    def _setup_action(self):
        # File Actions
        self._open_action = QAction(QIcon.fromTheme(QIcon.ThemeIcon.DocumentOpen), "Open", parent=self)
        self._open_action.setShortcuts(QKeySequence.StandardKey.Open)
        self._open_action.setIconVisibleInMenu(False)
        self._open_action.triggered.connect(self.open_database_triggered)

        self._close_action = QAction(self.tr("Close"), parent=self)
        self._close_action.setShortcuts(QKeySequence.StandardKey.Close)
        self._close_action.setIconVisibleInMenu(False)
        self._close_action.triggered.connect(self.close_database_triggered)

        self._quit_action = QAction(self.tr("Quit"), parent=self)
        self._quit_action.setShortcuts(QKeySequence.StandardKey.Quit)
        self._quit_action.setIconVisibleInMenu(False)
        self._quit_action.triggered.connect(QCoreApplication.quit, type=Qt.ConnectionType.QueuedConnection)

        self._toggle_inspect_dialog_action = QAction(self.tr("Get Info"), parent=self)
        self._toggle_inspect_dialog_action.setShortcut(
            QKeyCombination(Qt.KeyboardModifier.ControlModifier, Qt.Key.Key_I))
        self._toggle_inspect_dialog_action.triggered.connect(self._toggle_inspect_dialog_triggered)

        self._toggle_blobs_dialog_action = QAction(self.tr("Get Blobs"), parent=self)
        self._toggle_blobs_dialog_action.setShortcut(
            QKeyCombination(Qt.KeyboardModifier.ControlModifier, Qt.Key.Key_7))
        self._toggle_blobs_dialog_action.triggered.connect(self._toggle_blobs_dialog_triggered)

        self._reopen_last_database_action = QAction(self.tr("Reopen Last Database"), parent=self)
        self._reopen_last_database_action.setCheckable(True)
        self._reopen_last_database_action.triggered.connect(self._reopen_last_database_triggered)

        self._connect_to_server_action = QAction(self.tr("Connect To Server"), parent=self)
        self._connect_to_server_action.setShortcut(QKeyCombination(Qt.KeyboardModifier.ControlModifier, Qt.Key.Key_K))
        self._connect_to_server_action.triggered.connect(self._connect_to_server_triggered)

        # Help Actions — kept in the Help menu (NoRole) so macOS does not
        # migrate them into the application menu, matching the QML build.
        self._about_action = QAction(self.tr("About DB Editor..."), parent=self)
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
        file_menu.addAction(self._toggle_blobs_dialog_action)
        file_menu.addSeparator()
        file_menu.addAction(self._reopen_last_database_action)

        if platform.system() != "Darwin":
            file_menu.addSeparator()
            file_menu.addAction(self._quit_action)

        admin_menu = self.menuBar().addMenu(self.tr("&Admin"))
        admin_menu.addAction(self._connect_to_server_action)

        help_menu = self.menuBar().addMenu(self.tr("&Help"))
        help_menu.addAction(self._about_action)
        help_menu.addAction(self._about_qt_action)

        settings = DSSettings()
        checked = settings.reopen_last_file
        self._reopen_last_database_action.setChecked(checked)

    def _setup_central_widget(self):
        self._documents = DSDocumentsDatabasing()
        self.setCentralWidget(self._documents)

    # MARK: - Inspect
    ###############################################################################
    def _toggle_inspect_dialog_triggered(self):
        ds_dialog_helper.toggle(self._inspect_dialog, self._inspect_dialog_geometry)

    # MARK: - Blob
    def _toggle_blobs_dialog_triggered(self):
        ds_dialog_helper.toggle(self._blobs_dialog, self._blobs_dialog_geometry)

    def _inspect_database_did_open(self):
        inspect = self._inspect_dialog.inspect()
        inspect.set_path(self._database.path())
        inspect.set_documentation(self._database.documentation())
        inspect.set_uuid(self._database.uuid().encoded())
        inspect.set_codec_name(self._database.codec_name())
        inspect.set_definition_hexdigest(self._database.definitions_hexdigest())
        inspect.set_definitions(self._database.definitions())
        self._blobs_dialog.set_blob_getting(self._database.blob_getting())

    def _inspect_database_did_close(self):
        self._inspect_dialog.inspect().clear()
        self._blobs_dialog.unset_blob_getting()

    # MARK: - About
    ###############################################################################
    def _about_triggered(self):
        ds_license.show_about_dialog(self, "DB Editor", "Database Editor", version=__version__)

    # MARK: - Databasing
    ###############################################################################
    def _database_close(self):
        try:
            if self._database:
                self._database.close()
                self._database = None

            self._documents.clear()
            self._configure_window_title()
            self._validate_actions()
            self._inspect_database_did_close()

        except ViperError as e:
            self._except_present(e)

    # MARK: - Database
    ###############################################################################
    def open_database_triggered(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Open Document", self._databases_path, "All files (*.*) ;;")
        if not len(filename):
            return

        self._databases_path = QFileInfo(filename).filePath()
        self._set_database(filename)

    def close_database_triggered(self):
        self._database_close()

    def _reopen_last_database_triggered(self):
        checked = self._reopen_last_database_action.isChecked()
        settings = DSSettings()
        settings.reopen_last_file = checked
        settings.sync()

    def _set_database(self, filename: str):
        try:
            database = Database.open(filename)
            self.close_database_triggered()

            self._database = database
            self._configure_window_title()
            self._validate_actions()
            self._inspect_database_did_open()
            self._documents.set_database(self._database)

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

    # MARK: - Database Repository
    ###############################################################################
    def _connect_to_server_triggered(self):
        connect_dialog = DSConnectToServerDialog(parent=self)
        connect_dialog.exec()
        if connect_dialog.result() == QDialog.DialogCode.Rejected:
            return

        try:
            settings = DSSettings()
            host = settings.connect_hostname
            service = settings.connect_service
            socket_path = settings.connect_socket_path
            use_socket_path = settings.connect_use_socket_path

            if use_socket_path:
                databases = Database.databases_local(socket_path)
            else:
                databases = Database.databases(host, service)
            databases.sort()

            database_dialog = DSDatabaseSelectDialog(databases, parent=self)
            database_dialog.exec()
            if database_dialog.result() == QDialog.DialogCode.Rejected:
                return

            database = database_dialog.selected()
            if database:
                if use_socket_path:
                    self._set_database_repository(Database.connect_local(database, socket_path))
                else:
                    self._set_database_repository(Database.connect(database, host, service))

        except ViperError as e:
            self._except_present(e)

    def _set_database_repository(self, database: Database):
        try:
            self.close_database_triggered()
            self._database = database

            self._configure_window_title()
            self._validate_actions()
            self._inspect_database_did_open()
            self._documents.set_database(self._database)

        except ViperError as e:
            self._except_present(e)

    # MARK: - Actions
    ###############################################################################
    def _validate_actions(self):
        has_database = self._database is not None
        self._close_action.setEnabled(has_database)
        self._toggle_inspect_dialog_action.setEnabled(has_database)

    # MARK: - Title
    def _configure_window_title(self):
        title = "DB Editor (PySide)"

        if self._database:
            filename = os.path.basename(self._database.path())
            title = f'{title} - {filename}'

        self.setWindowTitle(title)

    # MARK: - Error
    def _except_present(self, e: ViperError):
        self._present_error(Error.parse(str(e)))

    def _present_error(self, error: Error):
        QMessageBox.critical(self, "Error", error.explained(),
                             QMessageBox.StandardButton.Ok,
                             QMessageBox.StandardButton.NoButton)


def main():
    Error.set_process_name("dbe")

    # Application
    app = QApplication(sys.argv)
    app.setApplicationDisplayName("DB Editor")
    app.setApplicationName("DB Editor")
    app.setApplicationVersion(__version__)
    app.setStyle("fusion")
    app.setWindowIcon(QIcon(":/images/dbe_icon.png"))

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
        if not Database.is_compatible(database_path):
            print(f'The SQL schema is not compatible with a Digital Substrate Database.')
            exit(1)

    # Window
    window = MainWindow()
    if database_path:
        window.set_bootstrap_database_path(database_path)
    window.show()
    app.exec()


if __name__ == '__main__':
    main()
