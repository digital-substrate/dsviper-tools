from __future__ import annotations

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QDialog, QTreeWidgetItem

from .ui_ds_documents_keys_dialog import Ui_DSDocumentsKeysDialog
from dsviper import AttachmentGetting, ValueKey, KeyNamer


class DSCommitDocumentsKeysDialog(QDialog, Ui_DSDocumentsKeysDialog):
    def __init__(self, keys: list[ValueKey], attachment_getting: AttachmentGetting, key_namer: KeyNamer, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)
        self._keys = keys
        self._attachment_getting = attachment_getting
        self._key_namer = key_namer

        self._configure_title()
        self._configure_ui()
        self._configure()
        self._setup_connections()

        self.setWindowIcon(QIcon(":/dsviper_components/images/app.png"))

    def selected_key(self) -> ValueKey | None:
        items = self.w_tree_widget.selectedItems()
        if len(items) == 0:
            return None

        row = self.w_tree_widget.indexFromItem(items[0]).row()
        return self._keys[row]

    def _setup_connections(self):
        self.w_ok_button.clicked.connect(self.accept)
        self.w_cancel_button.clicked.connect(self.reject)

    def _configure_ui(self):
        self.w_tree_widget.setColumnWidth(0, 300)

    def _configure_title(self):
        title = "Select Key"

        if len(self._keys):
            title = f'Select {self._keys[0].type().representation()}'

        self.setWindowTitle(title)

    def _configure(self):
        for key in self._keys:
            instance_id = key.instance_id().encoded()

            key_name = "-"
            if name := self._key_namer.smart_name(key, self._attachment_getting):
                key_name = name

            item = QTreeWidgetItem(self.w_tree_widget, [instance_id, key_name])
            item.setToolTip(0, key.detail_type_representation())
