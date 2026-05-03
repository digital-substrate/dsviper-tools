from PySide6.QtWidgets import QTreeWidget

from .ds_documents_comboxbox_item import DSDocumentsComboBoxItem
from .ds_documents_item import DSDocumentsItem
from .ds_helper import byte_count

from dsviper import (
    Value,
    ValueVoid,
    ValueBool,
    ValueUInt8, ValueUInt16, ValueUInt32, ValueUInt64,
    ValueInt8, ValueInt16, ValueInt32, ValueInt64,
    ValueFloat, ValueDouble,
    ValueCommitId, ValueBlobId, ValueUUId,
    ValueString, ValueBlob,
    ValueVec, ValueMat,
    ValueTuple,
    ValueOptional, ValueVector, ValueSet, ValueMap, ValueXArray,
    ValueAny, ValueVariant,
    ValueEnumeration, ValueStructure,
    ValueKey
)

from dsviper import Type, TypeTuple, TypeSet, TypeMap, TypeXArray, TypeVariant, TypeStructure
from dsviper import Attachment, Path, PathConst, AttachmentGetting, BlobGetting


class DSDocumentsBuilder:
    def __init__(self, key: ValueKey, attachment_getting: AttachmentGetting, blob_getting: BlobGetting):
        self._key = key
        self._attachment_getting = attachment_getting
        self._blob_getting = blob_getting

    def build(self, tree_widget: QTreeWidget, readonly: bool = False):
        tree_widget.blockSignals(True)
        tree_widget.clear()

        for key in ValueKey.keys(self._key):
            self._create_documents(key, tree_widget, readonly)

        tree_widget.blockSignals(False)

    def _build_primitive(self, key: ValueKey,
                         attachment: Attachment,
                         document: Value,
                         path: PathConst,
                         readonly: bool) -> DSDocumentsItem:

        item = DSDocumentsItem(DSDocumentsItem.TYPE_PRIMITIVE, key, attachment, document, path)
        item.is_container = False
        item.is_readonly = readonly

        value = item.value
        if isinstance(value, ValueBool):
            if readonly:
                item.string_value = value.representation()
            else:
                item.is_checked = value.encoded()
                item.is_readonly = True

        elif isinstance(value, ValueBlobId):
            item.is_readonly = True
            item.string_value = value.representation()
            if info := self._blob_getting.blob_info(value):
                vpr_type = value.type().representation()
                layout = info.blob_layout().representation()
                size = byte_count(info.size())
                tooltip = f'{vpr_type}\nLayout: {layout}\nSize: {size}'
                item.string_value_tool_tip = tooltip

        elif isinstance(value, ValueCommitId):
            item.is_readonly = True
            item.string_value = value.representation()

        elif isinstance(value, ValueBlob):
            item.is_readonly = True
            item.string_value = value.representation()

        elif isinstance(value, ValueString):
            item.string_value = value.encoded()

        else:
            item.string_value = value.representation()

        return item

    def _build_vec(self, key: ValueKey,
                   attachment: Attachment,
                   document: Value,
                   path: PathConst,
                   readonly: bool,
                   enumeration_items: list[DSDocumentsItem]) -> DSDocumentsItem:

        item = DSDocumentsItem(DSDocumentsItem.TYPE_VEC, key, attachment, document, path)
        item.is_readonly = readonly

        item.string_value = item.value.representation()
        value = ValueVec.cast(item.value)

        for index in range(len(value)):
            child_path = path.copy().index(index).const()
            child_item = self._build_item(key, attachment, document, child_path, item.is_readonly, enumeration_items)

            child_item.string_component = f'[{index}]'
            child_item.string_component_tool_tip = "uint64"
            child_item.string_value_tool_tip = value.type_vec().element_type().representation()

            item.insertChild(index, child_item)

        return item

    def _build_mat(self, key: ValueKey,
                   attachment: Attachment,
                   document: Value,
                   path: PathConst,
                   readonly: bool,
                   enumeration_items: list[DSDocumentsItem]) -> DSDocumentsItem:

        item = DSDocumentsItem(DSDocumentsItem.TYPE_MAT, key, attachment, document, path)
        item.is_readonly = readonly

        item.string_value = item.value.representation()
        value = ValueMat.cast(item.value)

        rows = value.type_mat().rows()
        for index in range(len(value)):
            child_path = path.copy().index(index).const()
            child_item = self._build_item(key, attachment, document, child_path, item.is_readonly, enumeration_items)

            col = index // rows
            row = index % rows

            child_item.string_component = f'[{col},{row}]'
            child_item.string_component_tool_tip = "uint64"
            child_item.string_value_tool_tip = value.type_mat().element_type().representation()

            item.insertChild(index, child_item)

        return item

    def _build_tuple(self, key: ValueKey,
                     attachment: Attachment,
                     document: Value,
                     path: PathConst,
                     readonly: bool,
                     enumeration_items: list[DSDocumentsItem]) -> DSDocumentsItem:
        item = DSDocumentsItem(DSDocumentsItem.TYPE_TUPLE, key, attachment, document, path)
        item.is_readonly = readonly
        item.string_value = item.value.representation()
        value = ValueTuple.cast(item.value)
        for index in range(len(value)):
            child_path = path.copy().index(index).const()
            child_item = self._build_item(key, attachment, document, child_path, item.is_readonly, enumeration_items)
            child_item.string_component = f'[{index}]'
            item.insertChild(index, child_item)

        return item

    def _build_optional(self, key: ValueKey,
                        attachment: Attachment,
                        document: Value,
                        path: PathConst,
                        readonly: bool,
                        enumeration_items: list[DSDocumentsItem]) -> DSDocumentsItem:

        item = DSDocumentsItem(DSDocumentsItem.TYPE_OPTIONAL, key, attachment, document, path)
        item.is_readonly = readonly

        value = ValueOptional.cast(item.value)
        item.string_value = "has no value." if value.is_nil() else "has a value."

        if not value.is_nil():
            child_path = path.copy().unwrap().const()
            child_item = self._build_item(key, attachment, document, child_path, item.is_readonly, enumeration_items)
            child_item.string_component = "unwrap()"
            item.insertChild(0, child_item)

        return item

    def _build_vector(self, key: ValueKey,
                      attachment: Attachment,
                      document: Value,
                      path: PathConst,
                      readonly: bool,
                      enumeration_items: list[DSDocumentsItem]) -> DSDocumentsItem:

        item = DSDocumentsItem(DSDocumentsItem.TYPE_VECTOR, key, attachment, document, path)
        item.is_readonly = readonly

        value = ValueVector.cast(item.value)
        item.string_value = f'{len(value)} {"elements" if len(value) else "element"}'

        for index in range(len(value)):
            child_path = path.copy().index(index).const()
            child_item = self._build_item(key, attachment, document, child_path, item.is_readonly, enumeration_items)

            child_item.string_component = f'[{index}]'
            child_item.string_component_tool_tip = "uint64"
            child_item.string_value_tool_tip = value.type_vector().element_type().representation()

            item.insertChild(index, child_item)

        return item

    def _build_set(self, key: ValueKey,
                   attachment: Attachment,
                   document: Value,
                   path: PathConst,
                   readonly: bool,
                   enumeration_items: list[DSDocumentsItem]) -> DSDocumentsItem:

        item = DSDocumentsItem(DSDocumentsItem.TYPE_SET, key, attachment, document, path)
        item.is_readonly = readonly

        # FIXME
        # bool notEditable {Viper::TypeHelper::useSetOrMap(value->typeSet->elementType)};

        value = ValueSet.cast(item.value)
        item.string_value = f'{len(value)} {"elements" if len(value) else "element"}'

        for index in range(len(value)):
            child_path = path.copy().element(index).const()
            child_item = self._build_item(key, attachment, document, child_path, item.is_readonly, enumeration_items)

            child_item.string_component = '-'
            child_item.string_component_tool_tip = value.type_set().element_type().representation()
            child_item.set_string_value_tool_tip = value.type_set().element_type().representation()

            item.insertChild(index, child_item)

        return item

    def _build_map_entry(self, key: ValueKey,
                         attachment: Attachment,
                         document: Value,
                         path: PathConst,
                         readonly: bool,
                         enumeration_items: list[DSDocumentsItem]) -> DSDocumentsItem:

        item = DSDocumentsItem(DSDocumentsItem.TYPE_MAP_ENTRY, key, attachment, document, path)
        item.is_readonly = readonly

        value = ValueTuple.cast(item.value)
        item.string_value = value.at(1, encoded=False).representation()

        map_path = path.parent().const()
        map_value = ValueMap.cast(map_path.at(document, encoded=False))

        key_path = path.copy().index(0).const()

        not_editable = self._use_set_or_map(map_value.type_map().key_type())
        key_item = self._build_item(key, attachment, document, key_path, (item.is_readonly or not_editable),
                                    enumeration_items)

        key_item.string_component = "key"
        key_item.string_component_tool_tip = map_value.type_map().key_type().representation()
        key_item.set_string_value_tool_tip = map_value.type_map().key_type().representation()
        item.insertChild(0, key_item)

        value_path = path.copy().index(1).const()
        value_item = self._build_item(key, attachment, document, value_path, item.is_readonly, enumeration_items)

        value_item.string_component = "value"
        value_item.string_component_tool_tip = map_value.type_map().element_type().representation()
        value_item.string_value_tool_tip = map_value.type_map().element_type().representation()
        item.insertChild(1, value_item)

        return item

    def _build_map(self, key: ValueKey,
                   attachment: Attachment,
                   document: Value,
                   path: PathConst,
                   readonly: bool,
                   enumeration_items: list[DSDocumentsItem]) -> DSDocumentsItem:

        item = DSDocumentsItem(DSDocumentsItem.TYPE_MAP, key, attachment, document, path)
        item.is_readonly = readonly

        value = ValueMap.cast(item.value)
        item.string_value = f'{len(value)} {"entries" if len(value) else "entry"}'

        for index, value_key in enumerate(value.keys(encoded=False)):
            child_path = path.copy().entry(value_key).const()
            child_item = self._build_map_entry(key, attachment, document, child_path, item.is_readonly,
                                               enumeration_items)

            child_item.string_component = f'[{value_key.representation()}]'
            child_item.string_component_tool_tip = value.type_map().key_type().representation()
            child_item.string_value_tool_tip = value.type_map().element_type().representation()
            item.insertChild(index, child_item)

        return item

    def _build_xarray(self, key: ValueKey,
                      attachment: Attachment,
                      document: Value,
                      path: PathConst,
                      readonly: bool,
                      enumeration_items: list[DSDocumentsItem]) -> DSDocumentsItem:

        item = DSDocumentsItem(DSDocumentsItem.TYPE_XARRAY, key, attachment, document, path)
        item.is_readonly = readonly
        value = ValueXArray.cast(item.value)
        item.string_value = f'{len(value)} {"elements" if len(value) else "element"}'

        for index, (position, _) in enumerate(value.items()):
            child_path = path.copy().position(position).const()
            child_item = self._build_item(key, attachment, document, child_path, item.is_readonly, enumeration_items)

            child_item.string_component = f'[{position.encoded()}]'
            child_item.string_component_tool_tip = "uuid"
            item.insertChild(index, child_item)

        return item

    def _build_any(self, key: ValueKey,
                   attachment: Attachment,
                   document: Value,
                   path: PathConst,
                   readonly: bool,
                   enumeration_items: list[DSDocumentsItem]) -> DSDocumentsItem:

        item = DSDocumentsItem(DSDocumentsItem.TYPE_ANY, key, attachment, document, path)
        item.is_readonly = readonly

        value = ValueAny.cast(item.value)
        if value.is_nil():
            item.string_value = "has no value."
        else:
            item.string_value = f'value is {value.unwrap(encoded=False).type().representation()}.'

        if not value.is_nil():
            child_path = path.copy().unwrap().const()
            child_item = self._build_item(key, attachment, document, child_path, item.is_readonly, enumeration_items)

            child_item.string_component = "unwrap()"
            item.insertChild(0, child_item)

        return item

    def _build_variant(self, key: ValueKey,
                       attachment: Attachment,
                       document: Value,
                       path: PathConst,
                       readonly: bool,
                       enumeration_items: list[DSDocumentsItem]) -> DSDocumentsItem:

        item = DSDocumentsItem(DSDocumentsItem.TYPE_VARIANT, key, attachment, document, path)
        item.is_readonly = readonly
        value = ValueVariant.cast(item.value)

        item.string_value = value.unwrap(encoded=False).type().representation()

        child_path = path.copy().unwrap().const()
        child_item = self._build_item(key, attachment, document, child_path, item.is_readonly, enumeration_items)

        child_item.string_component = "unwrap()"
        item.insertChild(0, child_item)

        return item

    def _build_enumeration(self, key: ValueKey,
                           attachment: Attachment,
                           document: Value,
                           path: PathConst,
                           readonly: bool,
                           enumeration_items: list[DSDocumentsItem]) -> DSDocumentsItem:
        item = DSDocumentsItem(DSDocumentsItem.TYPE_ENUMERATION, key, attachment, document, path)
        item.is_container = False
        item.is_readonly = readonly

        value = ValueEnumeration.cast(item.value)
        item.string_value = value.name()

        enumeration_items.append(item)
        return item

    def _build_structure(self, key: ValueKey,
                         attachment: Attachment,
                         document: Value,
                         path: PathConst,
                         readonly: bool,
                         enumeration_items: list[DSDocumentsItem]) -> DSDocumentsItem:
        item = DSDocumentsItem(DSDocumentsItem.TYPE_STRUCTURE, key, attachment, document, path)
        item.is_readonly = readonly

        value = ValueStructure.cast(item.value)
        if value.type_structure().is_compact():
            item.string_value = value.representation()

        for index, field in enumerate(value.type_structure().fields()):
            child_path = path.copy().field(field.name()).const()
            child_item = self._build_item(key, attachment, document, child_path, item.is_readonly, enumeration_items)
            child_item.string_component = field.name()
            item.insertChild(index, child_item)

        return item

    def _build_key(self, key: ValueKey,
                   attachment: Attachment,
                   document: Value,
                   path: PathConst) -> DSDocumentsItem:

        item = DSDocumentsItem(DSDocumentsItem.TYPE_KEY, key, attachment, document, path)
        item.is_container = False
        item.is_readonly = True

        value = ValueKey.cast(item.value)
        item.string_value = value.representation()
        item.string_value_tool_tip = value.detail_type_representation()

        return item

    def _build_item(self, key: ValueKey,
                    attachment: Attachment,
                    document: Value,
                    path: PathConst,
                    readonly: bool,
                    enumeration_items: list[DSDocumentsItem]) -> DSDocumentsItem:

        value = path.at(document, encoded=False)
        if isinstance(value, ValueVoid):
            return self._build_primitive(key, attachment, document, path, readonly)

        elif isinstance(value, ValueBool):
            return self._build_primitive(key, attachment, document, path, readonly)

        elif isinstance(value, ValueUInt8):
            return self._build_primitive(key, attachment, document, path, readonly)
        elif isinstance(value, ValueUInt16):
            return self._build_primitive(key, attachment, document, path, readonly)
        elif isinstance(value, ValueUInt32):
            return self._build_primitive(key, attachment, document, path, readonly)
        elif isinstance(value, ValueUInt64):
            return self._build_primitive(key, attachment, document, path, readonly)

        elif isinstance(value, ValueInt8):
            return self._build_primitive(key, attachment, document, path, readonly)
        elif isinstance(value, ValueInt16):
            return self._build_primitive(key, attachment, document, path, readonly)
        elif isinstance(value, ValueInt32):
            return self._build_primitive(key, attachment, document, path, readonly)
        elif isinstance(value, ValueInt64):
            return self._build_primitive(key, attachment, document, path, readonly)

        elif isinstance(value, ValueFloat):
            return self._build_primitive(key, attachment, document, path, readonly)
        elif isinstance(value, ValueDouble):
            return self._build_primitive(key, attachment, document, path, readonly)

        elif isinstance(value, ValueBlobId):
            return self._build_primitive(key, attachment, document, path, readonly)
        elif isinstance(value, ValueCommitId):
            return self._build_primitive(key, attachment, document, path, readonly)
        elif isinstance(value, ValueUUId):
            return self._build_primitive(key, attachment, document, path, readonly)

        elif isinstance(value, ValueString):
            return self._build_primitive(key, attachment, document, path, readonly)
        elif isinstance(value, ValueBlob):
            return self._build_primitive(key, attachment, document, path, readonly)

        elif isinstance(value, ValueVec):
            return self._build_vec(key, attachment, document, path, readonly, enumeration_items)
        elif isinstance(value, ValueMat):
            return self._build_mat(key, attachment, document, path, readonly, enumeration_items)

        elif isinstance(value, ValueTuple):
            return self._build_tuple(key, attachment, document, path, readonly, enumeration_items)
        elif isinstance(value, ValueOptional):
            return self._build_optional(key, attachment, document, path, readonly, enumeration_items)
        elif isinstance(value, ValueVector):
            return self._build_vector(key, attachment, document, path, readonly, enumeration_items)
        elif isinstance(value, ValueSet):
            return self._build_set(key, attachment, document, path, readonly, enumeration_items)
        elif isinstance(value, ValueMap):
            return self._build_map(key, attachment, document, path, readonly, enumeration_items)
        elif isinstance(value, ValueXArray):
            return self._build_xarray(key, attachment, document, path, readonly, enumeration_items)

        elif isinstance(value, ValueAny):
            return self._build_any(key, attachment, document, path, readonly, enumeration_items)
        elif isinstance(value, ValueVariant):
            return self._build_variant(key, attachment, document, path, readonly, enumeration_items)

        elif isinstance(value, ValueEnumeration):
            return self._build_enumeration(key, attachment, document, path, readonly, enumeration_items)
        elif isinstance(value, ValueStructure):
            return self._build_structure(key, attachment, document, path, readonly, enumeration_items)
        elif isinstance(value, ValueKey):
            return self._build_key(key, attachment, document, path)

        raise Exception(f'unhandled type {value.type()}')

    def _create_documents(self, key: ValueKey, tree_widget: QTreeWidget, readonly: bool):
        enumeration_items: list[DSDocumentsItem] = []

        # Create Document by attachments
        attachments = self._attachments(key)

        for index, attachment in enumerate(attachments):
            document = self._attachment_getting.get(attachment, key)
            if not document.is_nil():
                item = self._build_item(key, attachment, document.unwrap(encoded=False), Path().const(), readonly,
                                        enumeration_items)
                tree_widget.insertTopLevelItem(index, item)
                item.string_component = attachment.type_name().name()
                item.string_component_tool_tip = attachment.representation()

        for item in enumeration_items:
            combo = self._create_combo(item)
            tree_widget.setItemWidget(item, 1, combo)

    def _create_combo(self, item: DSDocumentsItem) -> DSDocumentsComboBoxItem:
        value = ValueEnumeration.cast(item.value)

        result = DSDocumentsComboBoxItem(item, 1)
        result.blockSignals(True)
        for case_ in value.type_enumeration().cases():
            result.addItem(case_.name())

        index = value.index()
        result.setCurrentIndex(index)
        result.blockSignals(False)

        return result

    def _attachments(self, key: ValueKey) -> list[Attachment]:
        result: list[Attachment] = []

        for attachment in self._attachment_getting.definitions().attachments():
            if attachment.type_key() == key.type_key():
                if self._attachment_getting.has(attachment, key):
                    result.append(attachment)

        result.sort(key=lambda a: a.type_name().name())
        return result

    def _use_set_or_map(self, vpr_type: Type):
        if isinstance(vpr_type, TypeTuple):
            for element_type in vpr_type.types():
                if self._use_set_or_map(element_type):
                    return True
            return False

        elif isinstance(vpr_type, TypeSet):
            return True

        elif isinstance(vpr_type, TypeMap):
            return True

        elif isinstance(vpr_type, TypeXArray):
            return self._use_set_or_map(vpr_type.element_type())

        elif isinstance(vpr_type, TypeVariant):
            for element_type in vpr_type.types():
                if self._use_set_or_map(element_type):
                    return True
            return False

        elif isinstance(vpr_type, TypeStructure):
            for field in vpr_type.fields():
                if self._use_set_or_map(field.type()):
                    return True
            return False

        return False
