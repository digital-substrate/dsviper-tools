from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QDialog, QHBoxLayout

from .ds_commit_actions import DSCommitActions

from dsviper import CommitStore


class DSCommitActionsDialog(QDialog):

    def __init__(self, store: CommitStore, *args, **kwargs):
        super().__init__(*args, **kwargs)

        component = DSCommitActions()
        component.set_store(store)

        layout = QHBoxLayout(self)
        layout.addWidget(component)
        self.setLayout(layout)

        self.setWindowIcon(QIcon(":/dsviper_components/images/app.png"))
        self.setWindowTitle("Actions")
