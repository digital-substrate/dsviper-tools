from PySide6.QtCore import Qt, QPoint, QByteArray
from PySide6.QtGui import QAction, QGuiApplication
from PySide6.QtWidgets import QFrame, QTreeWidgetItem, QAbstractItemView, QTreeWidget, QMenu, QDialog, QMessageBox, \
    QInputDialog

from .ui_ds_documents import Ui_DSDocuments

from .ds_documents_attachments_dialog import DSCommitDocumentsAttachmentsDialog
from .ds_documents_builder import DSDocumentsBuilder
from .ds_documents_item import DSDocumentsItem
from .ds_documents_keys_dialog import DSCommitDocumentsKeysDialog
from .ds_documents_navigation import DSDocumentsNavigation
from .ds_documents_selection import DSDocumentsSelection
from .ds_item_delegate_no_edit import DSItemDelegateNoEdit
from .ds_item_delegate_validate import DSItemDelegateValidate

from dsviper import Attachment, PathConst, ValueKey, ViperError, Error, ValueAny, Fuzzer
from dsviper import KeyNamer, AttachmentGetting, BlobGetting, KeyHelper

from dsviper import (
    Value,
    ValueBool,
    ValueUInt8, ValueUInt16, ValueUInt32, ValueUInt64, ValueInt8, ValueInt16, ValueInt32, ValueInt64,
    ValueFloat, ValueDouble,
    ValueBlobId, ValueCommitId, ValueUUId,
    ValueOptional, ValueSet, ValueVariant,
    ValueEnumeration
)

from dsviper import (
    Type,
    TypeBool,
    TypeUInt8, TypeUInt16, TypeUInt32, TypeUInt64,
    TypeInt8, TypeInt16, TypeInt32, TypeInt64,
    TypeFloat, TypeDouble,
    TypeBlobId, TypeCommitId, TypeUUId,
    TypeString, TypeBlob,
    TypeSet,
    TypeEnumeration,
    TypeKey,
    TypeConcept, TypeClub, TypeAnyConcept)

Abstractions = TypeConcept | TypeClub | TypeAnyConcept


class DSDocuments(QFrame, Ui_DSDocuments):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)

        self._abstractions: list[Abstractions] = []
        self._keys: list[ValueKey] = []
        self._key_namer: KeyNamer | None = None

        # Navigation
        self._navigation: DSDocumentsNavigation | None = None

        # Current State
        self._current_abstraction: Abstractions | None = None
        self._current_key: ValueKey | None = None
        self._current_attachment: Attachment | None = None
        self._current_path: PathConst | None = None

        self._tree_configure_ui()
        self._setup_connections()

    def get_selected_inspection(self):
        """Return (key, attachment, path) for the currently selected document tree node."""
        item = self._document_selected_item()
        if item:
            return item.key, item.attachment, item.path
        return self._current_key, None, None

    # Helper for better Type Hint
    ################################################################################
    def _set_current_path(self, path: PathConst):
        self._current_path = path

    def _reset_current_path(self):
        self._current_path = None

    # Interface
    ################################################################################
    def _attachment_getting(self) -> AttachmentGetting:
        raise NotImplementedError

    def _blob_getting(self) -> BlobGetting:
        raise NotImplementedError

    def use_key(self, key: ValueKey):
        self._set_key(key)

    ## MARK: - Selection
    ################################################################################
    def selection(self) -> DSDocumentsSelection | None:
        if item := self._document_selected_item():
            return DSDocumentsSelection(item.key, item.attachment, item.path)
        return None

    ## MARK: - Navigation
    ################################################################################
    def can_go_forward(self) -> bool:
        return self._navigation and self._navigation.can_go_forward

    def go_forward(self):
        if not self.can_go_forward():
            return

        self._navigation.go_forward()
        location = self._navigation.current_location
        self._set_key_attachment_path(location.key, location.attachment, location.path)

    def can_go_back(self) -> bool:
        return self._navigation and self._navigation.can_go_back

    def go_back(self):
        if not self.can_go_back():
            return

        self._navigation.go_back()
        location = self._navigation.current_location
        self._set_key_attachment_path(location.key, location.attachment, location.path)

    # MARK: - Connections
    ################################################################################
    def _setup_connections(self):
        self.w_abstraction_tree_widget.itemSelectionChanged.connect(self._abstraction_selection_changed)
        self.w_abstraction_tree_widget.customContextMenuRequested.connect(self._abstraction_custom_menu_requested)

        self.w_key_tree_widget.itemSelectionChanged.connect(self._key_selection_changed)
        self.w_key_tree_widget.customContextMenuRequested.connect(self._key_custom_menu_requested)

        self.w_document_tree_widget.itemSelectionChanged.connect(self._document_selection_changed)
        self.w_document_tree_widget.customContextMenuRequested.connect(self._document_custom_menu_requested)
        self.w_document_tree_widget.itemChanged.connect(self._document_item_changed,
                                                        type=Qt.ConnectionType.QueuedConnection)
        self.w_document_tree_widget.itemDoubleClicked.connect(self._document_item_double_clicked)

    # MARK: - Source
    ################################################################################
    def _database_did_open(self):
        self._key_namer = KeyNamer(self._attachment_getting().definitions())

        self._collect_abstractions_and_reload()
        if len(self._abstractions):
            self._current_abstraction = self._abstractions[0]

        self._collect_keys_and_reload()
        if len(self._keys):
            self._current_key = self._keys[0]

        self._update_abstraction_selection()
        self._update_key_selection()

    def _database_definitions_did_change(self):
        self._collect_abstractions_and_reload()
        self._collect_keys_and_reload()
        self._update_abstraction_selection()
        self._update_key_selection()

    def _database_state_did_change(self):
        self._collect_keys_and_reload()
        self._update_key_selection()
        self._update_document()

    def _database_did_close(self):
        self._abstractions.clear()
        self._keys.clear()

        self._key_namer = None
        self._navigation = None

        self._current_abstraction = None
        self._current_key = None
        self._current_attachment = None
        self._reset_current_path()

        self._tree_clear(self.w_abstraction_tree_widget)
        self._tree_clear(self.w_key_tree_widget)
        self._tree_clear(self.w_document_tree_widget)

    # MARK: - Abstraction
    ################################################################################
    def _abstraction_new_instance_triggered(self):
        action = self._sender_action()
        row = int(action.data())

        vpr_type = self._abstractions[row]
        instance_id = ValueUUId.create()
        attachments = KeyHelper.attachments(vpr_type, self._attachment_getting().definitions())

        dialog = DSCommitDocumentsAttachmentsDialog(instance_id, attachments, self)
        dialog.exec()

        if dialog.result() == QDialog.DialogCode.Rejected:
            return

        selected_attachments = dialog.selected_attachment()
        instance_id = dialog.instance_id

        self._create_attachments(vpr_type, instance_id, selected_attachments)

        self._database_state_did_change()
        if len(selected_attachments):
            key = selected_attachments[-1].create_key(instance_id)
            self._set_key(key)

    def _create_attachments(self, vpr_type: Type, instance_id, attachments: list[Attachment]):
        raise NotImplementedError

    def _abstraction_selection_changed(self):
        items = self.w_abstraction_tree_widget.selectedItems()
        if len(items):
            idx = self.w_abstraction_tree_widget.indexFromItem(items[0])
            self._current_abstraction = self._abstractions[idx.row()]
        else:
            self._current_abstraction = None

        self._navigation = None
        self._current_key = None
        self._current_attachment = None
        self._reset_current_path()

        self._collect_keys_and_reload()
        if len(self._keys):
            self._current_key = self._keys[0]

        self._update_key_selection()
        self._update_document()

    def _abstraction_custom_menu_requested(self, pos: QPoint):
        idx = self.w_abstraction_tree_widget.indexAt(pos)
        if not idx.isValid():
            return

        vpr_type = self._abstractions[idx.row()]
        if vpr_type.type_code() != 'concept':
            return

        menu = QMenu(self)
        action = QAction(f"New Instance of {vpr_type.representation()}", parent=menu)
        action.setData(idx.row())
        action.triggered.connect(self._abstraction_new_instance_triggered)

        menu.addAction(action)
        menu.exec(self.w_abstraction_tree_widget.mapToGlobal(pos))

    def _collect_abstractions_and_reload(self):
        self._collect_abstractions()

        tree_view = self.w_abstraction_tree_widget
        tree_view.blockSignals(True)
        tree_view.clear()

        for vpr_type in self._abstractions:
            QTreeWidgetItem(tree_view, [vpr_type.representation()])

    def _collect_abstractions(self):
        self._abstractions.clear()

        definitions = self._attachment_getting().definitions()
        for vpr_type in definitions.concepts():
            self._abstractions.append(vpr_type)

        for vpr_type in definitions.clubs():
            self._abstractions.append(vpr_type)

        for attachment in definitions.attachments():
            if attachment.key_type == Type.ANY_CONCEPT:
                self._abstractions.append(Type.ANY_CONCEPT)
                break

        self._abstractions.sort(key=lambda t: t.representation())

    def _update_abstraction_selection(self):
        if self._current_abstraction:
            for i, abstraction in enumerate(self._abstractions):
                if self._current_abstraction == abstraction:
                    self._tree_update_selection(self.w_abstraction_tree_widget, i)
        else:
            self._tree_update_clear_selection(self.w_abstraction_tree_widget)

    # MARK: - Keys
    ################################################################################
    def _key_selection_changed(self):
        items = self.w_key_tree_widget.selectedItems()
        if len(items):
            idx = self.w_key_tree_widget.indexFromItem(items[0])
            self._current_key = self._keys[idx.row()]
        else:
            self._current_key = None

        self._update_document()

    def _key_custom_menu_requested(self, pos: QPoint):
        idx = self.w_key_tree_widget.indexAt(pos)
        if not idx.isValid():
            return

        menu = QMenu(self)

        add_attachment_action = QAction("Add Attachments", parent=menu)
        add_attachment_action.setData(idx.row())
        add_attachment_action.triggered.connect(self._key_add_attachments_triggered)

        copy_key_instance_id_action = QAction("Copy Key Instance ID", parent=menu)
        copy_key_instance_id_action.setData(idx.row())
        copy_key_instance_id_action.triggered.connect(self._key_copy_identifier_triggered)

        find_key_instance_i_action = QAction("Find Key Instance ID", parent=menu)
        find_key_instance_i_action.triggered.connect(self._key_find_identifier_triggered)

        menu.addAction(add_attachment_action)
        menu.addAction(copy_key_instance_id_action)
        menu.addAction(find_key_instance_i_action)
        menu.exec(self.w_key_tree_widget.mapToGlobal(pos))

    def _key_add_attachments_triggered(self):
        action = self._sender_action()
        row = int(action.data())
        key = self._keys[row]

        instance_id = key.instance_id()
        attachments = KeyHelper.missing_attachments(key, self._attachment_getting())

        dialog = DSCommitDocumentsAttachmentsDialog(instance_id, attachments, self)
        dialog.disable_generate()
        dialog.exec()

        if dialog.result() == QDialog.DialogCode.Rejected:
            return

        self._create_attachments(key.type_concept(), instance_id, dialog.selected_attachment())

        self._database_state_did_change()
        if len(attachments):
            key = attachments[-1].create_key(instance_id)
            self._set_key(key)

    def _key_copy_identifier_triggered(self):
        action = self._sender_action()
        row = int(action.data())
        key = self._keys[row]
        QGuiApplication.clipboard().setText(key.instance_id().encoded())

    def _key_find_identifier_triggered(self):
        dlg = QInputDialog(self)
        dlg.setInputMode(QInputDialog.InputMode.TextInput)
        dlg.setWindowTitle("Find Key By Instance ID")
        dlg.setLabelText("Key Instance ID")
        dlg.resize(350, 100)

        if dlg.exec() == QDialog.DialogCode.Rejected:
            return

        uuid_string = dlg.textValue()
        instance_id = ValueUUId.try_parse(uuid_string)
        if instance_id is None:
            return

        found_key: ValueKey | None = None
        for key in self._keys:
            if key.instance_id() == instance_id:
                found_key = key
                break

        if found_key:
            self._set_key(found_key)

    def _collect_keys_and_reload(self):
        self._collect_keys()

        tree_view = self.w_key_tree_widget
        tree_view.blockSignals(True)
        tree_view.clear()

        for key in self._keys:
            instance_id = key.instance_id().encoded()
            name = self._name_for_key(key, "-")
            item = QTreeWidgetItem(tree_view, [instance_id, name])
            item.setToolTip(0, key.detail_type_representation())

        tree_view.blockSignals(False)

    def _collect_keys(self):
        self._keys.clear()

        if self._current_abstraction is None:
            return

        attachment_getting = self._attachment_getting()
        definitions = attachment_getting.definitions()
        type_key = TypeKey(self._current_abstraction)
        keys = ValueSet(TypeSet(type_key))
        for attachment in definitions.attachments():
            if attachment.type_key() == type_key:
                keys.update(attachment_getting.keys(attachment))

        for key in keys:
            self._keys.append(ValueKey.cast(key))

    def _update_key_selection(self):
        if self._current_key:
            for i, key in enumerate(self._keys):
                if self._current_key == key:
                    self._tree_update_selection(self.w_key_tree_widget, i)
                    break
        else:
            self._tree_update_clear_selection(self.w_key_tree_widget)

    def _set_key(self, key: ValueKey):
        if self._current_key and self._current_attachment and self._current_path and self._current_key.type_key() == key.type_key():
            self._set_key_attachment_path(key, self._current_attachment, self._current_path)
        else:
            self._set_key_attachment_path(key, None, None)

    def _set_key_attachment_path(self, key: ValueKey, attachment: Attachment | None, path: PathConst | None):
        self._current_abstraction = key.type_key().element_type()
        self._current_key = key
        self._current_attachment = attachment
        self._set_current_path(path)

        self._collect_keys_and_reload()
        self._update_abstraction_selection()
        self._update_key_selection()
        self._update_document()

    def _name_for_key(self, key: ValueKey, fallback: str) -> str:
        name = self._key_namer.smart_name(key, self._attachment_getting())
        return name if name else fallback

    # Mutations
    ################################################################################
    def _document_item_changed(self, item: DSDocumentsItem):
        try:
            if item.is_check_box:
                value = ValueBool(item.is_checked)
            else:
                vpr_type = item.value.type()
                str_repr = item.string_value
                value = self._value_from_representation(vpr_type, str_repr)

            self._commit_mutations(item, value)

        except ViperError as e:
            self._except_present(e)

    def _document_item_double_clicked(self, item: DSDocumentsItem):
        self._document_key_jump_to(item)

    def _commit_mutations(self, item: DSDocumentsItem, value: Value):
        self._set_current_path(item.path)

        if value == item.value:
            return

        if self._is_in_entry_key(item):
            self._commit_mutations_update_entry_key(item, value)

        elif self._is_in_element(item):
            self._commit_mutations_update_element(item, value)

        else:
            self._commit_mutations_update_or_set(item, value)

    def _is_in_entry_key(self, item: DSDocumentsItem):
        return item.path.is_entry_key_path()

    def _is_in_element(self, item: DSDocumentsItem):
        return item.path.is_element_path()

    # Context Menu Helpers
    @staticmethod
    def _menu_add_action(menu: QMenu, title: str, slot):
        action = QAction(title, parent=menu)
        action.triggered.connect(slot)
        menu.addAction(action)

    def _menu_for_optional(self, menu: QMenu, item: DSDocumentsItem):
        value_optional = ValueOptional.cast(item.value)
        if value_optional.is_nil():
            self._menu_add_action(menu, "Wrap Default", self._document_optional_wrap_default_triggered)
        else:
            self._menu_add_action(menu, "Clear", self._document_optional_clear_triggered)

    def _menu_for_set(self, menu: QMenu, item: DSDocumentsItem):
        from dsviper import TypeOptional, TypeVector, TypeVec, TypeMap, TypeXArray, TypeVariant, TypeAny
        value_set = ValueSet.cast(item.value)
        element_type = value_set.type_set().element_type()

        if isinstance(element_type, TypeKey):
            self._menu_add_action(menu, "Insert Key", self._document_set_insert_key_triggered)
        elif isinstance(element_type, (TypeOptional, TypeVector, TypeVec, TypeSet, TypeMap, TypeXArray, TypeVariant, TypeAny)):
            pass  # Block — created elements would be inert at element paths
        else:
            self._menu_add_action(menu, "Append", self._document_set_append_triggered)

    def _menu_for_variant(self, menu: QMenu, item: DSDocumentsItem):
        value_variant = ValueVariant.cast(item.value)
        for index, vpr_type in enumerate(value_variant.type_variant().types()):
            title = f'Reset to {vpr_type.representation()}'
            action = QAction(title, parent=menu)
            action.setData(index)
            action.triggered.connect(self._document_variant_reset_triggered)
            menu.addAction(action)

    def _menu_for_any(self, menu: QMenu, item: DSDocumentsItem):
        value_any = ValueAny.cast(item.value)
        definitions = self._attachment_getting().definitions()
        fuzzer = Fuzzer(definitions)

        if not value_any.is_nil():
            self._menu_add_action(menu, "Clear", self._document_any_clear_triggered)
            menu.addSeparator()

        for vpr_type in fuzzer.types():
            if isinstance(vpr_type, TypeBlob) or isinstance(vpr_type, TypeBlobId):
                continue

            action = QAction(f'Reset to {vpr_type.representation()}', parent=menu)
            action.triggered.connect(self._document_any_reset_triggered)
            blob = Type.encode(vpr_type)
            data = QByteArray()
            data.append(blob.encoded())
            action.setData(data)
            menu.addAction(action)

    def _commit_mutations_update_or_set(self, item: DSDocumentsItem, value: Value):
        raise NotImplementedError

    def _commit_mutations_update_entry_key(self, item: DSDocumentsItem, value: Value):
        raise NotImplementedError

    def _commit_mutations_update_element(self, item: DSDocumentsItem, value: Value):
        raise NotImplementedError

    # Documents
    ################################################################################
    def _document_selected_item(self) -> DSDocumentsItem | None:
        selected_items = self.w_document_tree_widget.selectedItems()
        return selected_items[0] if len(selected_items) else None

    def _document_selection_changed(self):
        item = self._document_selected_item()

        if item:
            self._current_attachment = item.attachment
            self._set_current_path(item.path)

            if self._navigation:
                location = self._navigation.current_location
                if location.key == item.key:
                    location.attachment = self._current_attachment
                    location.path = self._current_path
        else:
            self._current_attachment = None
            self._reset_current_path()

    def _document_custom_menu_requested(self, pos: QPoint):
        menu = QMenu(self)
        item = self._document_selected_item()

        if not item:
            self._document_menu_show(menu, pos)
            return

        if item.path.is_entry_key_path():
            return

        item_blocked = item.path.is_element_path()
        parent_blocked = item.parent_item is not None and item.parent_item.path.is_element_path()

        # Container operations — mutation uses item.path
        if not item_blocked:

            if item.type() == DSDocumentsItem.TYPE_OPTIONAL:
                self._menu_for_optional(menu, item)
                return self._document_menu_show(menu, pos)

            if item.type() == DSDocumentsItem.TYPE_VECTOR:
                self._menu_add_action(menu, "Append", self._document_vector_append_triggered)
                return self._document_menu_show(menu, pos)

            if item.type() == DSDocumentsItem.TYPE_SET:
                self._menu_for_set(menu, item)
                return self._document_menu_show(menu, pos)

            if item.type() == DSDocumentsItem.TYPE_MAP:
                self._menu_add_action(menu, "Append", self._document_map_append_triggered)
                return self._document_menu_show(menu, pos)

            if item.type() == DSDocumentsItem.TYPE_XARRAY:
                self._menu_add_action(menu, "Append", self._document_xarray_append_triggered)
                return self._document_menu_show(menu, pos)

            if item.type() == DSDocumentsItem.TYPE_VARIANT:
                self._menu_for_variant(menu, item)
                return self._document_menu_show(menu, pos)

            if item.type() == DSDocumentsItem.TYPE_ANY:
                self._menu_for_any(menu, item)
                return self._document_menu_show(menu, pos)

        # Child operations — mutation uses parent.path
        if not parent_blocked and item.parent_item:

            if item.parent_item.type() == DSDocumentsItem.TYPE_VECTOR:
                self._menu_add_action(menu, "Remove", self._document_vector_remove_triggered)
                self._menu_add_action(menu, "Insert", self._document_vector_insert_triggered)
                self._document_menu_key(menu, item)
                return self._document_menu_show(menu, pos)

            if item.parent_item.type() == DSDocumentsItem.TYPE_SET:
                self._menu_add_action(menu, "Remove", self._document_set_remove_triggered)
                self._document_menu_key(menu, item)
                return self._document_menu_show(menu, pos)

            if item.parent_item.type() == DSDocumentsItem.TYPE_MAP:
                self._menu_add_action(menu, "Remove", self._document_map_remove_triggered)
                self._document_menu_key(menu, item)
                return self._document_menu_show(menu, pos)

            if item.parent_item.type() == DSDocumentsItem.TYPE_XARRAY:
                self._menu_add_action(menu, "Remove", self._document_x_array_remove_triggered)
                self._menu_add_action(menu, "Insert", self._document_xarray_insert_triggered)
                self._document_menu_key(menu, item)
                return self._document_menu_show(menu, pos)

        self._document_menu_key(menu, item)
        return self._document_menu_show(menu, pos)

    def _update_document(self):
        if self._current_key is None:
            self._tree_clear(self.w_document_tree_widget)
            return

        builder = DSDocumentsBuilder(self._current_key,
                                     self._attachment_getting(),
                                     self._blob_getting())

        builder.build(self.w_document_tree_widget)
        self._expand_path()

    # MARK: - Actions
    ################################################################################
    def _document_action_toggle_column_triggered(self):
        action = self._sender_action()
        column = int(action.data())

        if self.w_document_tree_widget.isColumnHidden(column):
            self.w_document_tree_widget.showColumn(column)
        else:
            self.w_document_tree_widget.hideColumn(column)

    # MARK: - Optional Actions
    ################################################################################
    def _document_optional_wrap_default_triggered(self):
        raise NotImplementedError

    def _document_optional_clear_triggered(self):
        raise NotImplementedError

    # MARK: - Vector Actions
    ################################################################################
    def _document_vector_append_triggered(self):
        raise NotImplementedError

    def _document_vector_insert_triggered(self):
        raise NotImplementedError

    def _document_vector_remove_triggered(self):
        raise NotImplementedError

    # MARK: - Set Actions
    ################################################################################
    def _document_set_insert_key_triggered(self):
        raise NotImplementedError

    def _document_select_key(self) -> ValueKey | None:
        item = self._document_selected_item()
        if item.type() != DSDocumentsItem.TYPE_SET:
            return None

        value_set = ValueSet.cast(item.value)
        type_key = TypeKey.cast(value_set.type_set().element_type())
        attachment_getting = self._attachment_getting()
        keys = KeyHelper.collect_keys(type_key, attachment_getting)
        keys.difference_update(value_set)

        dialog = DSCommitDocumentsKeysDialog(list(keys), attachment_getting, self._key_namer, self)
        dialog.exec()

        if dialog.result() == QDialog.DialogCode.Rejected:
            return None

        return dialog.selected_key()

    def _document_set_append_triggered(self):
        raise NotImplementedError

    def _document_set_remove_triggered(self):
        raise NotImplementedError

    # MARK: - Map Actions
    ################################################################################
    def _document_map_append_triggered(self):
        raise NotImplementedError

    def _document_map_remove_triggered(self):
        raise NotImplementedError

    # MARK: - XArray Actions
    ################################################################################
    def _document_xarray_append_triggered(self):
        raise NotImplementedError

    def _document_x_array_remove_triggered(self):
        raise NotImplementedError

    def _document_xarray_insert_triggered(self):
        raise NotImplementedError

    # MARK: - Variant Actions
    ################################################################################
    def _document_variant_reset_triggered(self):
        raise NotImplementedError

    # MARK: - Any Actions
    ################################################################################
    def _document_any_clear_triggered(self):
        raise NotImplementedError

    def _document_any_reset_triggered(self):
        raise NotImplementedError

    # MARK: - Key Actions
    ################################################################################
    def _document_key_jump_to(self, item: DSDocumentsItem):
        if item.type() != DSDocumentsItem.TYPE_KEY:
            return

        key = ValueKey.cast(item.value)
        if not key.instance_id().is_valid():
            return

        go_key = key.to_concept_key()
        if self._navigation is None:
            self._navigation = DSDocumentsNavigation(item.key, item.attachment, item.path)
        elif self._navigation.current_index == 0:
            self._navigation = DSDocumentsNavigation(item.key, item.attachment, item.path)

        # update Location
        location = self._navigation.current_location
        if location.key == item.key:
            location.attachment = item.attachment
            location.path = item.path

        self._navigation.push(go_key, None, None)
        self._set_key(go_key)

    def _document_key_jump_to_triggered(self):
        self._document_key_jump_to(self._document_selected_item())

    def _document_key_copy_triggered(self):
        item = self._document_selected_item()
        if item.type() != DSDocumentsItem.TYPE_KEY:
            return

        key = ValueKey.cast(item.value)
        QGuiApplication.clipboard().setText(key.instance_id().encoded())

    def _document_menu_show(self, menu: QMenu, pos: QPoint):
        toggle_path_column_action = QAction(
            f'{"Show" if self.w_document_tree_widget.isColumnHidden(2) else "Hide"} Column Path',
            parent=menu)
        toggle_path_column_action.setData(2)
        toggle_path_column_action.triggered.connect(self._document_action_toggle_column_triggered)

        toggle_type_column_action = QAction(
            f'{"Show" if self.w_document_tree_widget.isColumnHidden(3) else "Hide"} Column Type',
            parent=menu)
        toggle_type_column_action.setData(3)
        toggle_type_column_action.triggered.connect(self._document_action_toggle_column_triggered)

        if not menu.isEmpty():
            menu.addSeparator()

        menu.addAction(toggle_path_column_action)
        menu.addAction(toggle_type_column_action)

        menu.exec(self.w_document_tree_widget.mapToGlobal(pos))

    def _document_key_select_triggered(self):
        item = self._document_selected_item()
        if item.type() != DSDocumentsItem.TYPE_KEY:
            return

        attachment_getting = self._attachment_getting()
        key = ValueKey.cast(item.value)
        keys = KeyHelper.collect_keys(key.type_key(), attachment_getting)
        keys.discard(key)

        dialog = DSCommitDocumentsKeysDialog(list(keys), attachment_getting, self._key_namer, self)
        dialog.exec()

        if dialog.result() == QDialog.DialogCode.Rejected:
            return

        selected_key = dialog.selected_key()
        if not selected_key:
            return

        self._commit_mutations(item, selected_key)

    def _document_menu_key(self, menu: QMenu, item: DSDocumentsItem):
        if item.type() != DSDocumentsItem.TYPE_KEY:
            return

        if not menu.isEmpty():
            menu.addSeparator()

        select_action = QAction("Set Key", parent=menu)
        select_action.triggered.connect(self._document_key_select_triggered)
        menu.addAction(select_action)

        key = ValueKey.cast(item.value)
        if key.instance_id().is_valid():
            jump_action = QAction("Jump To Key", parent=menu)
            jump_action.triggered.connect(self._document_key_jump_to_triggered)
            menu.addAction(jump_action)

        copy_action = QAction("Copy Key Instance ID", parent=menu)
        copy_action.triggered.connect(self._document_key_copy_triggered)
        menu.addAction(copy_action)

    # MARK: - Expand Path
    ################################################################################
    def _expand_path(self):
        three_widget = self.w_document_tree_widget
        if three_widget.topLevelItemCount() == 0:
            return

        is_resolved = False
        if self._current_path and self._current_attachment:
            count = three_widget.topLevelItemCount()
            for i in range(count):
                item: DSDocumentsItem = three_widget.topLevelItem(i)
                if item.attachment.runtime_id() == self._current_attachment.runtime_id():
                    is_resolved = self._expand_path_item(self._current_path, item)
                    if is_resolved:
                        break

        if not is_resolved and three_widget.topLevelItemCount() == 1:
            three_widget.expandItem(three_widget.topLevelItem(0))

    def _expand_path_item(self, path: PathConst, item: DSDocumentsItem):
        w_item = item
        ancestors = path.ancestors()
        ancestors.pop()
        while len(ancestors):
            search_path = ancestors[-1]
            child_item = self._child_item(w_item, search_path.const())
            if child_item:
                ancestors.pop()
                w_item = child_item
            else:
                break

        w_expand_item = w_item
        item_to_expand: list[DSDocumentsItem] = []
        while w_expand_item:
            item_to_expand.insert(0, w_expand_item)
            w_expand_item = w_expand_item.parent_item

        for item in item_to_expand:
            self.w_document_tree_widget.expandItem(item)

        is_resolved = len(ancestors) == 0
        if is_resolved:
            self.w_document_tree_widget.setCurrentItem(w_item)
            self.w_document_tree_widget.scrollToItem(w_item)

        return is_resolved

    def _child_item(self, item: DSDocumentsItem, path: PathConst):
        count = item.childCount()
        for i in range(count):
            child_item = item.child_item(i)
            child_path = child_item.path
            if child_path == path:
                return child_item
        return None

    # MARK: - TreeView Helper
    ################################################################################
    def _tree_configure_ui(self):
        self.w_abstraction_tree_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.w_key_tree_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.w_key_tree_widget.setColumnWidth(0, 300)

        w_tw = self.w_document_tree_widget
        w_tw.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        w_tw.setEditTriggers(QAbstractItemView.EditTrigger.EditKeyPressed | QAbstractItemView.EditTrigger.DoubleClicked)
        w_tw.setItemDelegateForColumn(0, DSItemDelegateNoEdit(w_tw))
        w_tw.setItemDelegateForColumn(1, DSItemDelegateValidate(w_tw))
        w_tw.setItemDelegateForColumn(2, DSItemDelegateNoEdit(w_tw))
        w_tw.setItemDelegateForColumn(3, DSItemDelegateNoEdit(w_tw))
        w_tw.hideColumn(2)
        w_tw.hideColumn(3)
        w_tw.setColumnWidth(0, 200)

    def _tree_clear(self, tree_widget: QTreeWidget):
        tree_widget.blockSignals(True)
        tree_widget.clear()
        tree_widget.blockSignals(False)

    def _tree_update_selection(self, tree_widget: QTreeWidget, row: int):
        tree_widget.blockSignals(True)
        idx = tree_widget.model().index(row, 0, tree_widget.rootIndex())
        tree_widget.setCurrentIndex(idx)
        tree_widget.blockSignals(False)

    def _tree_update_clear_selection(self, tree_widget: QTreeWidget):
        tree_widget.blockSignals(True)
        tree_widget.clearSelection()
        tree_widget.blockSignals(False)

    ## MARK: Representation
    ################################################################################
    def _value_from_representation(self, vpr_type: Type, str_repr: str) -> Value | None:
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

        elif isinstance(vpr_type, TypeBlobId):
            return ValueBlobId.try_parse(str_repr)
        elif isinstance(vpr_type, TypeCommitId):
            return ValueCommitId.try_parse(str_repr)
        elif isinstance(vpr_type, TypeUUId):
            return ValueUUId.try_parse(str_repr)

        elif isinstance(vpr_type, TypeString):
            return Value.create(Type.STRING, str_repr)

        elif isinstance(vpr_type, TypeEnumeration):
            return ValueEnumeration.try_parse(str_repr, vpr_type)

        return None

    ## MARK: Error
    ################################################################################
    def _except_present(self, e: ViperError):
        self._present_error(Error.parse(str(e)))

    def _present_error(self, error: Error):
        QMessageBox.critical(self, "Error", error.explained(),
                             QMessageBox.StandardButton.Ok,
                             QMessageBox.StandardButton.NoButton)

    ## MARK: Action
    ################################################################################
    def _sender_action(self) -> QAction:
        return self.sender()
