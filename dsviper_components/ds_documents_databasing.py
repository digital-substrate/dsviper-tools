from __future__ import annotations

from .ds_documents import DSDocuments
from .ds_documents_item import DSDocumentsItem
from dsviper import Database, AttachmentGetting, BlobGetting, Attachment, ViperError
from dsviper import Type, Value, ValueUUId, ValueBlob, ValueOptional, ValueVector, ValueSet, ValueMap, ValueXArray, \
    ValueAny, ValueVariant, ValueKey


class DSDocumentsDatabasing(DSDocuments):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._database: Database | None = None

    # MARK: Interface
    ################################################################################
    def _attachment_getting(self) -> AttachmentGetting:
        return self._database.attachment_getting()

    def _blob_getting(self) -> BlobGetting:
        return self._database.blob_getting()

    ## MARK: - Databasing
    ################################################################################
    def set_database(self, database: Database):
        self._database = database
        self._database_did_open()
        self._database_state_did_change()

    def clear(self):
        self._database = None
        self._database_did_close()

    def _database_commit(self, attachment: Attachment, key: ValueKey, document: Value):
        try:
            self._database.begin_transaction()
            self._database.set(attachment, key, document)
            self._database.commit()
            self._database_state_did_change()

        except ViperError as e:
            self._database.rollback()
            self._except_present(e)

    # MARK: - Attachments
    ################################################################################
    def _create_attachments(self, vpr_type, instance_id: ValueUUId, attachments: list[Attachment]):
        try:
            self._database.begin_transaction()

            for attachment in attachments:
                key = attachment.create_key(instance_id)
                doc = attachment.create_document()
                self._database.set(attachment, key, doc)

            self._database.commit()

        except ViperError as e:
            self._database.rollback()
            self._except_present(e)

    # Commit Mutations
    ################################################################################
    def _commit_mutations_update_or_set(self, item: DSDocumentsItem, value: Value):
        try:
            path = item.path.regularized().const()
            path.set(item.document, value)

            # Mutations
            self._database_commit(item.attachment, item.key, item.document)

        except ViperError as e:
            self._except_present(e)

    def _commit_mutations_update_entry_key(self, item: DSDocumentsItem, value: Value):
        try:
            path = item.path
            info = path.entry_key_info()

            value_map = ValueMap.cast(info.map_path().at(item.document))
            current_value = value_map.at(info.key(), encoded=False)
            if info.key_path().is_root():
                new_key = value
            else:
                new_key = info.key()
                info.key_path().set(new_key, value)

            self._set_current_path(info.map_path().copy().entry(new_key).index(0).path(info.key_path()).const())

            # Mutations
            value_map.remove(info.key())
            value_map.set(new_key, current_value)
            self._database_commit(item.attachment, item.key, item.document)

        except ViperError as e:
            self._except_present(e)

    def _commit_mutations_update_element(self, item: DSDocumentsItem, value: Value):
        try:
            path = item.path
            info = path.element_info()

            value_set = ValueSet.cast(info.set_path().at(item.document))
            current_value = value_set.at(info.index())

            if info.element_path().is_root():
                new_value = Value.copy(value)
            else:
                new_value = Value.copy(current_value)
                info.element_path().set(new_value, value)

            if index := value_set.index(new_value):
                self._set_current_path(info.set_path().copy().element(index).path(info.element_path()).const())

            # Mutations
            value_set.remove(current_value)
            value_set.add(new_value)

            self._database_commit(item.attachment, item.key, item.document)

        except ViperError as e:
            self._except_present(e)

    # MARK: - Optional Actions
    ################################################################################
    def _document_optional_wrap_default_triggered(self):
        item = self._document_selected_item()
        try:
            optional = ValueOptional.cast(item.value)
            self._set_current_path(item.path.copy().unwrap().const())

            # Mutations
            value = ValueOptional(optional.type_optional(), Value.create(optional.type_optional().element_type()))
            item.path.regularized().set(item.document, value)
            self._database_commit(item.attachment, item.key, item.document)

        except ViperError as e:
            self._except_present(e)

    def _document_optional_clear_triggered(self):
        item = self._document_selected_item()
        try:
            # Mutations
            ValueOptional.cast(item.path.regularized().const().at(item.document)).clear()
            self._database_commit(item.attachment, item.key, item.document)

        except ViperError as e:
            self._except_present(e)

    # MARK: - Vector Actions
    ################################################################################
    def _document_vector_append_triggered(self):
        item = self._document_selected_item()
        vector = ValueVector.cast(item.value)
        self._set_current_path(item.path.copy().index(len(vector)).const())

        # Mutations
        vector.append(Value.create(vector.type_vector().element_type()))
        self._database_commit(item.attachment, item.key, item.document)

    def _document_vector_insert_triggered(self):
        item = self._document_selected_item()
        index = item.parent_item.indexOfChild(item)

        try:
            value_vector = ValueVector.cast(item.parent_item.value)
            value_vector.insert(index, Value.create(value_vector.type_vector().element_type()))

            # Mutations
            self._database_commit(item.attachment, item.key, item.document)

        except ViperError as e:
            self._except_present(e)

    def _document_vector_remove_triggered(self):
        item = self._document_selected_item()
        index = item.parent_item.indexOfChild(item)

        try:
            vector = ValueVector.cast(item.parent_item.value)
            if len(vector) == 1:
                self._set_current_path(item.parent_item.path)
            else:
                if index == len(vector) - 1:
                    index += -1
                self._set_current_path(item.parent_item.path.copy().index(index).const())

            # Mutations
            vector.pop(index)
            self._database_commit(item.attachment, item.key, item.document)

        except ViperError as e:
            self._except_present(e)

    # MARK: - Set Actions
    ################################################################################
    def _document_set_insert_key_triggered(self):
        item = self._document_selected_item()
        selected_key = self._document_select_key()
        if not selected_key:
            return

        try:
            value_set = ValueSet.cast(item.value)
            value_set.add(selected_key)
            if index := value_set.index(selected_key):
                self._set_current_path(item.path.copy().element(index).const())

            # Mutations
            self._database_commit(item.attachment, item.key, item.document)

        except ViperError as e:
            self._except_present(e)

    def _document_set_append_triggered(self):
        item = self._document_selected_item()
        value_set = ValueSet.cast(item.value)
        if len(value_set) == 0:
            v = Value.create(value_set.type_set().element_type())
        else:
            v = Value.succ(value_set.max(encoded=False))

        self._set_current_path(item.path.copy().element(len(value_set)).const())

        # Mutations
        value_set.add(v)
        self._database_commit(item.attachment, item.key, item.document)

    def _document_set_remove_triggered(self):
        item = self._document_selected_item()
        try:
            value_set = ValueSet.cast(item.parent_item.value)
            if len(value_set) == 1:
                self._set_current_path(item.parent_item.path)

            # Mutations
            value_set.remove(item.value)
            self._database_commit(item.attachment, item.key, item.document)

        except ViperError as e:
            self._except_present(e)

    # MARK: - Map Actions
    ################################################################################
    def _document_map_append_triggered(self):
        item = self._document_selected_item()
        try:
            value_map = ValueMap.cast(item.value)
            if len(value_map) == 0:
                new_key = Value.create(value_map.type_map().key_type())
            else:
                new_key = Value.succ(value_map.max(encoded=False))

            new_value = Value.create(value_map.type_map().element_type())

            self._set_current_path(item.path.copy().entry(new_key).index(0).const())

            # Mutations
            value_map[new_key] = new_value
            self._database_commit(item.attachment, item.key, item.document)

        except ViperError as e:
            self._except_present(e)

    def _document_map_remove_triggered(self):
        item = self._document_selected_item()
        try:
            value_map = ValueMap.cast(item.parent_item.value)
            if len(value_map) == 1:
                self._set_current_path(item.parent_item.path)
            else:
                index = item.parent_item.indexOfChild(item)
                if index == 0:
                    selected_item = item.parent_item.child_item(1)
                else:
                    selected_item = item.parent_item.child_item(index - 1)
                self._set_current_path(selected_item.path)

            key = item.path.last_component_value(encoded=False)

            # Mutations
            value_map.remove(key)
            self._database_commit(item.attachment, item.key, item.document)

        except ViperError as e:
            self._except_present(e)

    # MARK: - XArray Actions
    ################################################################################
    def _document_xarray_append_triggered(self):
        item = self._document_selected_item()
        try:
            value_xarray = ValueXArray.cast(item.value)
            before_position = ValueXArray.end()
            new_position = ValueUUId.create()
            value = Value.create(value_xarray.type_xarray().element_type())

            self._set_current_path(item.path.copy().position(new_position).const())

            # Mutations
            value_xarray.insert(before_position, value, new_position)
            self._database_commit(item.attachment, item.key, item.document)

        except ViperError as e:
            self._except_present(e)

    def _document_x_array_remove_triggered(self):
        item = self._document_selected_item()
        try:
            position = ValueUUId.cast(item.path.last_component_value(encoded=False))

            if item.parent_item.childCount() == 1:
                self._set_current_path(item.parent_item.path)
            else:
                index = item.parent_item.indexOfChild(item)
                if index == 0:
                    selected_item = item.parent_item.child_item(1)
                else:
                    selected_item = item.parent_item.child_item(index - 1)

                self._set_current_path(selected_item.path)

            # Mutations
            value_xarray = ValueXArray.cast(item.parent_item.value)
            value_xarray.remove(position)
            self._database_commit(item.attachment, item.key, item.document)

        except ViperError as e:
            self._except_present(e)

    def _document_xarray_insert_triggered(self):
        item = self._document_selected_item()
        try:
            xarray_value = ValueXArray.cast(item.parent_item.value)
            before_position = ValueUUId.cast(item.path.last_component_value(encoded=False))
            new_position = ValueUUId.create()
            value = Value.create(xarray_value.type_xarray().element_type())

            self._set_current_path(item.parent_item.path.copy().position(new_position).const())

            # Mutations
            xarray_value.insert(before_position, value, new_position)
            self._database_commit(item.attachment, item.key, item.document)

        except ViperError as e:
            self._except_present(e)

    # MARK: - Variant Actions
    ################################################################################
    def _document_variant_reset_triggered(self):
        item = self._document_selected_item()
        try:
            action = self._sender_action()
            index = int(action.data())

            variant = ValueVariant.cast(item.value)
            vpr_type = variant.type_variant().types()[index]

            self._set_current_path(item.path.copy().unwrap().const())

            # Mutations
            variant.wrap(Value.create(vpr_type))
            self._database_commit(item.attachment, item.key, item.document)

        except ViperError as e:
            self._except_present(e)

    # MARK: - Any Actions
    ################################################################################
    def _document_any_clear_triggered(self):
        item = self._document_selected_item()
        try:
            value = ValueAny.cast(item.value)
            value.clear()

            # Mutations
            self._database_commit(item.attachment, item.key, item.document)

        except ViperError as e:
            self._except_present(e)

    def _document_any_reset_triggered(self):
        item = self._document_selected_item()
        action = self._sender_action()
        try:
            definitions = self._database.definitions()
            blob = ValueBlob(bytes(action.data()))
            vpr_type = Type.decode(blob, definitions)

            self._set_current_path(item.path.copy().unwrap().const())

            # Mutations
            value = ValueAny.cast(item.value)
            value.wrap(Value.create(vpr_type))
            self._database_commit(item.attachment, item.key, item.document)

        except ViperError as e:
            self._except_present(e)
