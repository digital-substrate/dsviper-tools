from PySide6.QtWidgets import QDialog, QHBoxLayout
from PySide6.QtGui import QIcon

from .ds_connect_to_server import DSConnectToServer


class DSConnectToServerDialog(QDialog):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        component = DSConnectToServer()

        layout = QHBoxLayout(self)
        layout.addWidget(component)
        self.setLayout(layout)

        self.setWindowIcon(QIcon(":/dsviper_components/images/app.png"))
        self.setWindowTitle("Connect To Server")

        component.ok_clicked.connect(self.accept)
        component.cancel_clicked.connect(self.reject)
