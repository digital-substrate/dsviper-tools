from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QDialog, QHBoxLayout

from .ds_commit_blobs import DSCommitBlobs

from dsviper import CommitStore


class DSCommitBlobsDialog(QDialog):

    def __init__(self, store: CommitStore, *args, **kwargs):
        super().__init__(*args, **kwargs)

        component = DSCommitBlobs()
        component.set_store(store)

        layout = QHBoxLayout(self)
        layout.addWidget(component)
        self.setLayout(layout)

        self.setWindowIcon(QIcon(":/dsviper_components/images/app.png"))
        self.setWindowTitle("Blobs")
