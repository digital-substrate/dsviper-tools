from __future__ import annotations

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QDialog, QHBoxLayout

from dsviper_components.ds_code_editor import DSCodeEditor
from dsviper_components.python_editor_model import PythonEditorModel


class DSCodeEditorDialog(QDialog):

    def __init__(self, model: PythonEditorModel, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._editor = DSCodeEditor(model)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._editor)
        self.setLayout(layout)

        self.setWindowIcon(QIcon(":/dsviper_components/images/app.png"))
        self.setWindowTitle("Python Editor")
        self.resize(900, 700)

    @property
    def editor(self) -> DSCodeEditor:
        return self._editor
