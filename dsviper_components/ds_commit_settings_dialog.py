from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QDialog, QHBoxLayout

from .ds_commit_settings import DSCommitSettings


class DSCommitSettingsDialog(QDialog):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        component = DSCommitSettings()

        layout = QHBoxLayout(self)
        layout.addWidget(component)
        self.setLayout(layout)

        self.setWindowIcon(QIcon(":/dsviper_components/images/app.png"))
        self.setWindowTitle("Settings")

        component.ok_clicked.connect(self.accept)
        component.cancel_clicked.connect(self.reject)
