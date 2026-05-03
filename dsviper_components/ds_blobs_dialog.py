from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QDialog, QHBoxLayout

from .ds_blobs import DSBlobs

from dsviper import BlobGetting


class DSBlobsDialog(QDialog):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._component = DSBlobs()

        layout = QHBoxLayout(self)
        layout.addWidget(self._component)
        self.setLayout(layout)

        self.setWindowIcon(QIcon(":/dsviper_components/images/app.png"))
        self.setWindowTitle("Blobs")

    def set_blob_getting(self, blob_getting: BlobGetting):
        self._component.set_blob_getting(blob_getting)

    def unset_blob_getting(self):
        self._component.unset_blob_getting()
