from __future__ import annotations

from PySide6.QtWidgets import QStyledItemDelegate, QTreeWidget, QLineEdit

from .ds_documents_item import DSDocumentsItem

from dsviper import (
    Type,
    TypeBool,
    TypeUInt8, TypeUInt16, TypeUInt32, TypeUInt64,
    TypeInt8, TypeInt16, TypeInt32, TypeInt64,
    TypeFloat, TypeDouble,
    TypeUUId, TypeBlobId, TypeString
)

from dsviper import (
    Value,
    ValueBool,
    ValueUInt8, ValueUInt16, ValueUInt32, ValueUInt64, ValueInt8, ValueInt16, ValueInt32, ValueInt64,
    ValueFloat, ValueDouble, ValueUUId, ValueBlobId, ValueString
)


class DSItemDelegateValidate(QStyledItemDelegate):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def setModelData(self, editor, model, index):
        tree_widget: QTreeWidget = self.parent()
        line_edit: QLineEdit = editor
        item: DSDocumentsItem = tree_widget.itemFromIndex(index)

        str_repr = line_edit.text()
        vpr_type = item.value.type()

        if self._is_valid(vpr_type, str_repr) is not None:
            super().setModelData(editor, model, index)

    def _is_valid(self, vpr_type: Type, str_repr: str) -> Value | None:
        if not len(str_repr):
            return None

        if isinstance(vpr_type, TypeBool):
            return ValueBool.try_parse(str_repr)

        elif isinstance(vpr_type, TypeUInt8):
            return ValueUInt8.try_parse(str_repr)
        elif isinstance(vpr_type, TypeUInt16):
            return ValueUInt16.try_parse(str_repr)
        elif isinstance(vpr_type, TypeUInt32):
            return ValueUInt32.try_parse(str_repr)
        elif isinstance(vpr_type, TypeUInt64):
            return ValueUInt64.try_parse(str_repr)

        elif isinstance(vpr_type, TypeInt8):
            return ValueInt8.try_parse(str_repr)
        elif isinstance(vpr_type, TypeInt16):
            return ValueInt16.try_parse(str_repr)
        elif isinstance(vpr_type, TypeInt32):
            return ValueInt32.try_parse(str_repr)
        elif isinstance(vpr_type, TypeInt64):
            return ValueInt64.try_parse(str_repr)

        elif isinstance(vpr_type, TypeFloat):
            return ValueFloat.try_parse(str_repr)
        elif isinstance(vpr_type, TypeDouble):
            return ValueDouble.try_parse(str_repr)

        elif isinstance(vpr_type, TypeUUId):
            return ValueUUId.try_parse(str_repr)
        elif isinstance(vpr_type, TypeBlobId):
            return ValueBlobId.try_parse(str_repr)

        elif isinstance(vpr_type, TypeString):
            return ValueString(str_repr)

        return None
