from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QDialog, QHBoxLayout

from .ds_commit_program import DSCommitProgram

from dsviper import CommitStore


class DSCommitProgramDialog(QDialog):

    def __init__(self, store: CommitStore, *args, **kwargs):
        super().__init__(*args, **kwargs)

        component = DSCommitProgram()
        component.set_store(store)

        layout = QHBoxLayout(self)
        layout.addWidget(component)
        self.setLayout(layout)

        self.setWindowIcon(QIcon(":/dsviper_components/images/app.png"))
        self.setWindowTitle("Program")
