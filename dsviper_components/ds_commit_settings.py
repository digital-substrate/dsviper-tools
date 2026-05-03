from __future__ import annotations

from PySide6.QtCore import Qt, Signal, QDir
from PySide6.QtGui import QGuiApplication, QIcon
from PySide6.QtWidgets import QFrame, QFileDialog

from .ds_commit_synchronization_source import DSCommitSynchronizationSource
from .ds_settings import DSSettings
from .ui_ds_commit_settings import Ui_DSCommitSettings

from dsviper import CommitStore


class DSCommitSettings(QFrame, Ui_DSCommitSettings):
    ok_clicked = Signal()
    cancel_clicked = Signal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)
        self._store: CommitStore | None = None

        self._configure()
        self._setup_connections()

        dark = "-dark" if QGuiApplication.styleHints().colorScheme() == Qt.ColorScheme.Dark else ""
        icon = QIcon(f':/dsviper_components/images/arrowshape.right.circle{dark}')

        self.w_sync_file_button.setIcon(icon)
        self.w_sync_socket_button.setIcon(icon)
        self.tabwidget.tabBar().setTabText(0, "Secondary Source")
        self.tabwidget.tabBar().setTabText(1, "Live Session")

    def _setup_connections(self):
        self.w_sync_file_button.clicked.connect(self._select_file_clicked)
        self.w_sync_socket_button.clicked.connect(self._select_socket_clicked)
        self.w_ok_button.clicked.connect(self._ok_clicked)
        self.w_cancel_button.clicked.connect(self._cancel_clicked)
        self.w_sync_source_combo_box.activated.connect(self._source_activated)

    def _ok_clicked(self):
        self._update()
        self.ok_clicked.emit()

    def _cancel_clicked(self):
        self.cancel_clicked.emit()

    def _select_file_clicked(self):
        path = QDir.homePath() + "/Databases/"
        filename, _ = QFileDialog.getOpenFileName(self, "Open Document", path, "All files (*.*) ;;")
        if not filename:
            return

        self.w_sync_file_label.setText(filename)

    def _select_socket_clicked(self):
        path = QDir.homePath() + "/Databases/"
        filename, _ = QFileDialog.getOpenFileName(self, "Open Document", path, "All files (*.sock) ;;")
        if filename is None:
            return

        self.w_sync_socket_label.setText(filename)

    def _source_activated(self):
        self._configure_source()

    def _configure(self):
        settings = DSSettings()
        self.w_sync_source_combo_box.setCurrentIndex(settings.sync_source)
        self.w_sync_file_label.setText(settings.sync_file_path)
        self.w_sync_socket_label.setText(settings.sync_socket_path)
        self.w_sync_hostname_line_edit.setText(settings.sync_hostname)
        self.w_sync_service_line_edit.setText(settings.sync_service)

        live_update_interval = settings.live_update_interval
        self.w_live_update_interval_spin_box.setValue(float(live_update_interval) / 10.0)
        self.w_live_sync_with_source_check_box.setChecked(settings.live_sync_with_source)

        self._configure_source()

    def _configure_source(self):
        self.w_sync_file_label.setEnabled(False)
        self.w_sync_file_button.setEnabled(False)

        self.w_sync_socket_label.setEnabled(False)
        self.w_sync_socket_button.setEnabled(False)

        self.w_sync_hostname_line_edit.setEnabled(False)
        self.w_sync_service_line_edit.setEnabled(False)

        current_index = self.w_sync_source_combo_box.currentIndex()
        if current_index == DSCommitSynchronizationSource.FILE.value:
            self.w_sync_file_label.setEnabled(True)
            self.w_sync_file_button.setEnabled(True)

        elif current_index == DSCommitSynchronizationSource.SOCKET.value:
            self.w_sync_socket_label.setEnabled(True)
            self.w_sync_socket_button.setEnabled(True)

        elif current_index == DSCommitSynchronizationSource.HOST.value:
            self.w_sync_hostname_line_edit.setEnabled(True)
            self.w_sync_service_line_edit.setEnabled(True)

    def _update(self):
        settings = DSSettings()

        settings.sync_source = self.w_sync_source_combo_box.currentIndex()
        settings.sync_hostname = self.w_sync_hostname_line_edit.text()
        settings.sync_service = self.w_sync_service_line_edit.text()
        settings.sync_socket_path = self.w_sync_socket_label.text()
        settings.sync_file_path = self.w_sync_file_label.text()
        settings.sync_socket_path = self.w_sync_socket_label.text()
        settings.live_update_interval = int(self.w_live_update_interval_spin_box.value() * 10)
        settings.live_sync_with_source = self.w_live_sync_with_source_check_box.isChecked()

        settings.sync()
