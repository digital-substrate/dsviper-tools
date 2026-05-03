from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QGuiApplication
from PySide6.QtWidgets import QDialog, QMessageBox, QTreeWidgetItem

from .ui_ds_documents_attachments_dialog import Ui_DSDocumentsAttachmentsDialog
from dsviper import ValueUUId, Attachment

class DSCommitDocumentsAttachmentsDialog(QDialog, Ui_DSDocumentsAttachmentsDialog):
    def __init__(self, instance_id: ValueUUId, attachments: list[Attachment], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)
        self._instance_id = instance_id
        self._attachments = attachments
        self._attachments.sort(key=lambda a: a.type_name().name())

        self._configure_icons()
        self._configure_identifier()
        self._configure()

        self._setup_connections()

        self.setWindowIcon(QIcon(":/dsviper_components/images/app.png"))
        self.setWindowTitle("Create Attachments")

    @property
    def instance_id(self):
        return self._instance_id

    def selected_attachment(self) -> list[Attachment]:
        result: list[Attachment] = []

        for index, attachment in enumerate(self._attachments):
            idx = self.w_tree_widget.model().index(index, 0, self.w_tree_widget.rootIndex())
            item = self.w_tree_widget.itemFromIndex(idx)
            if item.checkState(0) == Qt.CheckState.Checked:
                result.append(self._attachments[index])

        return result

    def disable_generate(self):
        self.w_generate_button.setEnabled(False)
        self.w_instance_line_edit.setEnabled(False)

    def _generate_identifier(self):
        self._instance_id = ValueUUId.create()
        self.w_instance_line_edit.setText(self._instance_id.encoded())

    def _identifier_return_pressed(self):
        try:
            candidate = ValueUUId.create(str(self.w_instance_line_edit.text()))
            self._instance_id = candidate
        except:
            QMessageBox.critical(self, "UUID ", "Not a valid Instance ID",
                                 QMessageBox.StandardButton.Ok,
                                 QMessageBox.StandardButton.NoButton)

    def _setup_connections(self):
        self.w_generate_button.clicked.connect(self._generate_identifier)
        self.w_instance_line_edit.returnPressed.connect(self._identifier_return_pressed)
        self.w_create_button.clicked.connect(self.accept)
        self.w_cancel_button.clicked.connect(self.reject)

    def _configure_icons(self):
        dark = "-dark" if QGuiApplication.styleHints().colorScheme() == Qt.ColorScheme.Dark else ""
        icon = QIcon(f':/dsviper_components/images/dice{dark}')
        self.w_generate_button.setIcon(icon)

    def _configure_identifier(self):
        self.w_instance_line_edit.blockSignals(True)
        self.w_instance_line_edit.setText(self._instance_id.encoded())
        self.w_instance_line_edit.blockSignals(False)

    def _configure(self):
        for attachment in self._attachments:
            item = QTreeWidgetItem(self.w_tree_widget, [attachment.type_name().name()])
            item.setToolTip(0, attachment.representation())
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(0, Qt.CheckState.Checked)
