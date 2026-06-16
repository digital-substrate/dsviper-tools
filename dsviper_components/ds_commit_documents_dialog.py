from PySide6.QtWidgets import QDialog, QHBoxLayout
from PySide6.QtGui import QIcon

from .ds_documents_commit_store import DSDocumentsCommitStore

from dsviper import CommitStore


class DSCommitDocumentsDialog(QDialog):

    def __init__(self, store: CommitStore, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._component = DSDocumentsCommitStore()
        self._component.set_store(store)

        layout = QHBoxLayout(self)
        layout.addWidget(self._component)
        self.setLayout(layout)

        self.setWindowIcon(QIcon(":/dsviper_components/images/app.png"))
        self.setWindowTitle("Documents")

    def documents(self) -> DSDocumentsCommitStore:
        return self._component
