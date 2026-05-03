from PySide6.QtWidgets import QDialog, QHBoxLayout
from PySide6.QtGui import QIcon

from .ds_commit_undo import DSCommitUndo

from dsviper import CommitStore


class DSCommitUndoDialog(QDialog):

    def __init__(self, store: CommitStore, *args, **kwargs):
        super().__init__(*args, **kwargs)

        component = DSCommitUndo()
        component.set_store(store)

        layout = QHBoxLayout(self)
        layout.addWidget(component)
        self.setLayout(layout)

        self.setWindowIcon(QIcon(":/dsviper_components/images/app.png"))
        self.setWindowTitle("Undo")
