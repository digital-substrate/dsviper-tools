from PySide6.QtWidgets import QDialog, QHBoxLayout
from PySide6.QtGui import QIcon

from .ds_inspect import DSInspect

class DSInspectDialog(QDialog):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._inspect = DSInspect()

        layout = QHBoxLayout(self)
        layout.addWidget(self._inspect)
        self.setLayout(layout)

        self.setWindowIcon(QIcon(":/dsviper_components/images/app.png"))
        self.setWindowTitle("Inspect")

    def inspect(self) -> DSInspect:
        return self._inspect