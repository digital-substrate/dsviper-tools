from __future__ import annotations

from .ds_commit_store_notifier import DSCommitStoreNotifier
from .ds_documents import DSDocuments
from .ds_documents_item import DSDocumentsItem
from dsviper import CommitStore, ViperError, Attachment, AttachmentGetting, BlobGetting
from dsviper import Type, TypeSet, Value, ValueUUId, ValueBlob, ValueOptional, ValueVector, ValueSet, ValueMap, ValueXArray, ValueAny, ValueVariant

class DSDocumentsCommitStore(DSDocuments):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._store: CommitStore | None = None
        self._setup_store_connections()

    # MARK: Interface
    ################################################################################
    def _attachment_getting(self) -> AttachmentGetting:
        return self._store.attachment_getting()

    def _blob_getting(self) -> BlobGetting:
        return self._store.database().blob_getting()

    ## MARK: - Commit Store
    ################################################################################
    def set_store(self, store: CommitStore):
        self._store = store

    def _setup_store_connections(self):
        notifier = DSCommitStoreNotifier.instance()
        notifier.database_did_open.connect(self._database_did_open)
        notifier.database_did_close.connect(self._database_did_close)
        notifier.definitions_did_change.connect(self._database_definitions_did_change)
        notifier.state_did_change.connect(self._database_state_did_change)

    # MARK: - Attachments
    ################################################################################
    def _create_attachments(self, vpr_type: Type, instance_id: ValueUUId, attachments: list[Attachment]):
        try:

            mutable_state = self._store.mutable_state()

            for attachment in attachments:
                key = attachment.create_key(instance_id)
                doc = attachment.create_document()
                mutable_state.attachment_mutating().set(attachment, key, doc)

            self._store.commit_mutations( f'New instance of {vpr_type.representation()}', mutable_state)

        except ViperError as e:
            self._except_present(e)

    # Commits Mutations
    ################################################################################
    def _commit_mutations_update_or_set(self, item: DSDocumentsItem, value: Value):
        try:
            path = item.path.regularized().const()
            mutable_state = self._store.mutable_state()

            if path.is_root():
                label = f'Set {value.representation()}'
                mutable_state.attachment_mutating().set(item.attachment, item.key, value)
            else:
                label = "Update " + path.last_component().representation() + " To " + value.representation()
                mutable_state.attachment_mutating().update(item.attachment, item.key, path, value)

            # Mutations
            self._store.commit_mutations(label, mutable_state)

        except ViperError as e:
            self._except_present(e)

    def _commit_mutations_update_entry_key(self, item: DSDocumentsItem, value: Value):
        try:
            path = item.path
            info = path.entry_key_info()

            value_map = ValueMap.cast(info.map_path().at(item.document))
            if info.key_path().is_root():
                new_key = value
            else:
                new_key = info.key()
                info.key_path().set(new_key, value)

            self._set_current_path(info.map_path().copy().entry(new_key).index(0).path(info.key_path()).const())

            # Mutations
            subtract_set = ValueSet(value_map.type_map().keys_type())
            subtract_set.add(info.key())

            union_map = ValueMap(value_map.type_map())
            union_map[new_key] = value_map[info.key()]

            mutable_state = self._store.mutable_state()
            map_path = info.map_path().regularized().const()
            mutable_state.attachment_mutating().subtract_in_map(item.attachment, item.key, map_path, subtract_set)
            mutable_state.attachment_mutating().union_in_map(item.attachment, item.key, map_path, union_map)
            self._store.commit_mutations("Update Key in Map", mutable_state)

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
            subtract_set = ValueSet(value_set.type_set())
            subtract_set.add(current_value)

            union_set = ValueSet(value_set.type_set())
            union_set.add(new_value)

            value_set.remove(current_value)
            value_set.add(new_value)

            mutable_state = self._store.mutable_state()
            set_path = info.set_path().regularized().const()
            mutable_state.attachment_mutating().subtract_in_set(item.attachment, item.key, set_path, subtract_set)
            mutable_state.attachment_mutating().union_in_set(item.attachment, item.key, set_path, union_set)
            self._store.commit_mutations("Update Element in Set", mutable_state)

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
            path = item.path.regularized().const()
            mutable_state = self._store.mutable_state()
            mutable_state.attachment_mutating().update(item.attachment, item.key, path, value)
            self._store.commit_mutations("Reset an Optional", mutable_state)

        except ViperError as e:
            self._except_present(e)

    def _document_optional_clear_triggered(self):
        item = self._document_selected_item()
        try:
            # Mutations
            value = ValueOptional.cast(item.value)
            value.clear()
            path = item.path.regularized().const()
            mutable_state = self._store.mutable_state()
            mutable_state.attachment_mutating().update(item.attachment, item.key, path, value)
            self._store.commit_mutations("Clear an Optional", mutable_state)

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
        path = item.path.regularized().const()
        mutable_state = self._store.mutable_state()
        mutable_state.attachment_mutating().update(item.attachment, item.key, path, vector)
        self._store.commit_mutations("Append in Vector", mutable_state)

    def _document_vector_insert_triggered(self):
        item = self._document_selected_item()
        index = item.parent_item.indexOfChild(item)
        try:
            value_vector = ValueVector.cast(item.parent_item.value)
            value_vector.insert(index, Value.create(value_vector.type_vector().element_type()))

            # Mutations
            path = item.parent_item.path.regularized().const()
            mutable_state = self._store.mutable_state()
            mutable_state.attachment_mutating().update(item.attachment, item.key, path, value_vector)
            self._store.commit_mutations("Insert in Vector", mutable_state)

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
            path = item.parent_item.path.regularized().const()
            mutable_state = self._store.mutable_state()
            mutable_state.attachment_mutating().update(item.attachment, item.key, path, vector)
            self._store.commit_mutations("Remove in Vector", mutable_state)

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
            union_set = ValueSet(value_set.type_set())
            union_set.add(selected_key)

            path = item.path.regularized().const()
            mutable_state = self._store.mutable_state()
            mutable_state.attachment_mutating().union_in_set(item.attachment, item.key, path, union_set)
            self._store.commit_mutations("Insert a Key", mutable_state)

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
        union_set = ValueSet(value_set.type_set())
        union_set.add(v)
        path = item.path.regularized().const()
        mutable_state = self._store.mutable_state()
        mutable_state.attachment_mutating().union_in_set(item.attachment, item.key, path, union_set)
        self._store.commit_mutations("Insert in Set", mutable_state)

    def _document_set_remove_triggered(self):
        item = self._document_selected_item()
        try:
            value_set = ValueSet.cast(item.parent_item.value)
            if len(value_set) == 1:
                self._set_current_path(item.parent_item.path)

            # Mutations
            union_set = ValueSet(value_set.type_set())
            union_set.add(item.value)

            path = item.parent_item.path.regularized().const()
            mutable_state = self._store.mutable_state()
            mutable_state.attachment_mutating().subtract_in_set(item.attachment, item.key, path, union_set)
            self._store.commit_mutations("Subtract in Set", mutable_state)

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
            union_map = ValueMap(value_map.type_map())
            union_map[new_key] = new_value

            path = item.path.regularized().const()
            mutable_state = self._store.mutable_state()
            mutable_state.attachment_mutating().union_in_map(item.attachment, item.key, path, union_map)
            self._store.commit_mutations("Append in Map", mutable_state)

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
            subtract_set = ValueSet(value_map.type_map().keys_type())
            subtract_set.add(key)

            path = item.parent_item.path.regularized().const()
            mutable_state = self._store.mutable_state()
            mutable_state.attachment_mutating().subtract_in_map(item.attachment, item.key, path, subtract_set)
            self._store.commit_mutations("Subtract in Map", mutable_state)

        except ViperError as e:
            self._except_present(e)

    # MARK: - XArray Actions
    ################################################################################
    def _document_xarray_append_triggered(self):
        item = self._document_selected_item()
        try:
            value_xarray = ValueXArray.cast(item.value)
            before_position = ValueXArray.END
            new_position = ValueUUId.create()
            value = Value.create(value_xarray.type_xarray().element_type())

            self._set_current_path(item.path.copy().position(new_position).const())

            # Mutations
            path = item.path.regularized().const()
            mutable_state = self._store.mutable_state()
            mutable_state.attachment_mutating().insert_in_xarray(item.attachment, item.key, path, before_position, new_position, value)
            self._store.commit_mutations("Append in XArray", mutable_state)

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
            path = item.parent_item.path.regularized().const()
            mutable_state = self._store.mutable_state()
            mutable_state.attachment_mutating().remove_in_xarray(item.attachment, item.key, path, position)
            self._store.commit_mutations("Remove In XArray", mutable_state)

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
            path = item.parent_item.path.regularized().const()
            mutable_state = self._store.mutable_state()
            mutable_state.attachment_mutating().insert_in_xarray(item.attachment, item.key, path, before_position,
                                                      new_position, value)
            self._store.commit_mutations("Insert in XArray", mutable_state)

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
            value = ValueVariant(variant.type_variant(), Value.create(vpr_type))
            path = item.path.regularized().const()
            mutable_state = self._store.mutable_state()
            mutable_state.attachment_mutating().update(item.attachment, item.key, path, value)
            self._store.commit_mutations(f"Reset a Variant to {vpr_type.representation()}", mutable_state)

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
            path = item.path.regularized().const()
            mutable_state = self._store.mutable_state()
            mutable_state.attachment_mutating().update(item.attachment, item.key, path, value)
            self._store.commit_mutations("Clear an Any", mutable_state)

        except ViperError as e:
            self._except_present(e)

    def _document_any_reset_triggered(self):
        item = self._document_selected_item()
        action = self._sender_action()
        try:
            definitions = self._store.database().definitions()
            blob = ValueBlob(bytes(action.data()))
            vpr_type = Type.decode(blob, definitions)

            self._set_current_path(item.path.copy().unwrap().const())

            # Mutations
            value = ValueAny(Value.create(vpr_type))
            path = item.path.regularized().const()
            mutable_state = self._store.mutable_state()
            mutable_state.attachment_mutating().update(item.attachment, item.key, path, value)
            self._store.commit_mutations("Reset an Any to {vpr_type.vpr_representation", mutable_state)

        except ViperError as e:
            self._except_present(e)
