from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QFrame

from .ds_settings import DSSettings
from .ui_ds_connect_to_server import Ui_DSConnectToServer


class DSConnectToServer(QFrame, Ui_DSConnectToServer):
    ok_clicked = Signal()
    cancel_clicked = Signal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)

        self._configure()
        self.w_ok_button.clicked.connect(self._ok_clicked)
        self.w_cancel_button.clicked.connect(self._cancel_clicked)

    def _ok_clicked(self):
        self._update()
        self.ok_clicked.emit()

    def _cancel_clicked(self):
        self.cancel_clicked.emit()

    def _configure(self):
        settings = DSSettings()

        self.w_host_line_edit.setText(settings.connect_hostname)
        self.w_service_line_edit.setText(settings.connect_service)
        self.w_socket_path_line_edit.setText(settings.connect_socket_path)
        self.w_use_socket_path_check_box.setChecked(settings.connect_use_socket_path)

    def _update(self):
        settings = DSSettings()
        settings.connect_hostname = self.w_host_line_edit.text()
        settings.connect_service = self.w_service_line_edit.text()
        settings.connect_socket_path = self.w_socket_path_line_edit.text()
        settings.connect_use_socket_path = self.w_use_socket_path_check_box.isChecked()
        settings.sync()
