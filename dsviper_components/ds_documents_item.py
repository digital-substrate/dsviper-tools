from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QTreeWidgetItem

from dsviper import Attachment, PathConst, Value, ValueKey

class DSDocumentsItem(QTreeWidgetItem):
    COLUMN_COMPONENT = 0
    COLUMN_VALUE = 1
    COLUMN_PATH = 2
    COLUMN_TYPE = 3

    TYPE_PRIMITIVE = 1001
    TYPE_VEC = 1002
    TYPE_MAT = 1003
    TYPE_TUPLE = 1004
    TYPE_OPTIONAL = 1005
    TYPE_VECTOR = 1006
    TYPE_SET = 1007
    TYPE_MAP = 1008
    TYPE_MAP_ENTRY = 1009
    TYPE_XARRAY = 1010
    TYPE_ANY = 1011
    TYPE_VARIANT = 1012
    TYPE_ENUMERATION = 1013
    TYPE_STRUCTURE = 1014
    TYPE_KEY = 1015

    def __init__(self, item_type: int, key: ValueKey, attachment: Attachment, document: Value, path: PathConst, *args,
                 **kwargs):
        super().__init__(type=item_type, *args, **kwargs)
        self._key = key
        self._attachment = attachment
        self._document = document
        self._path = path
        self._value = path.at(document, encoded=False)
        self._is_container = True
        self._is_read_only = True
        self.setFlags(self.flags() & ~Qt.ItemFlag.ItemIsUserCheckable)

        self.setText(self.COLUMN_COMPONENT, "-")
        self.setText(self.COLUMN_VALUE, "-")
        self.setText(self.COLUMN_PATH, path.representation())
        self.setText(self.COLUMN_TYPE, self._value.type().representation())

        self.setToolTip(self.COLUMN_COMPONENT, self.string_type)
        self.setToolTip(self.COLUMN_VALUE, self.string_type)

    @property
    def key(self) -> ValueKey:
        return self._key

    @property
    def attachment(self) -> Attachment:
        return self._attachment

    @property
    def document(self) -> Value:
        return self._document

    @property
    def path(self) -> PathConst:
        return self._path

    @property
    def value(self) -> Value:
        return self._value

    @property
    def parent_item(self) -> DSDocumentsItem | None:
        return self.parent()

    def child_item(self, index: int) -> DSDocumentsItem:
        return self.child(index)

    @property
    def string_component(self) -> str:
        return self.text(self.COLUMN_COMPONENT)

    @string_component.setter
    def string_component(self, value: str) -> None:
        self.setText(self.COLUMN_COMPONENT, value)

    @property
    def string_value(self) -> str:
        return self.text(self.COLUMN_VALUE)

    @string_value.setter
    def string_value(self, value: str):
        self.setText(self.COLUMN_VALUE, value)

    @property
    def string_type(self) -> str:
        return self.text(self.COLUMN_TYPE)

    @property
    def string_path(self) -> str:
        return self.text(self.COLUMN_PATH)

    @property
    def string_component_tool_tip(self) -> str:
        return self.toolTip(self.COLUMN_COMPONENT)

    @string_component_tool_tip.setter
    def string_component_tool_tip(self, value: str):
        self.setToolTip(self.COLUMN_COMPONENT, value)

    @property
    def string_value_tool_tip(self) -> str:
        return self.toolTip(self.COLUMN_VALUE)

    @string_value_tool_tip.setter
    def string_value_tool_tip(self, value: str):
        self.setToolTip(self.COLUMN_VALUE, value)

    @property
    def is_container(self):
        return self._is_container

    @is_container.setter
    def is_container(self, value: bool):
        self._is_container = value
        self._update_flags()

    @property
    def is_readonly(self):
        return self._is_read_only

    @is_readonly.setter
    def is_readonly(self, value: bool):
        self._is_read_only = value
        self._update_flags()

    @property
    def is_editable(self):
        return not self.is_container and not self.is_readonly

    @property
    def is_check_box(self):
        return (self.flags() & Qt.ItemFlag.ItemIsUserCheckable) == Qt.ItemFlag.ItemIsUserCheckable

    @property
    def is_checked(self):
        return self.checkState(self.COLUMN_VALUE) == Qt.CheckState.Checked

    @is_checked.setter
    def is_checked(self, enabled: bool):
        self.string_value = ""
        self.setFlags(self.flags() | Qt.ItemFlag.ItemIsUserCheckable)
        state = Qt.CheckState.Checked if enabled else Qt.CheckState.Unchecked
        self.setCheckState(self.COLUMN_VALUE, state)

    def _update_flags(self):
        flgs = self.flags()
        if self.is_editable:
            flgs |= Qt.ItemFlag.ItemIsEditable
        else:
            flgs &= ~Qt.ItemFlag.ItemIsEditable

        self.setFlags(flgs)
