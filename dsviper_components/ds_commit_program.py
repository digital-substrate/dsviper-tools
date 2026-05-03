from __future__ import annotations

from PySide6.QtCore import QDateTime
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QFrame, QLabel, QTreeWidgetItem

from .ui_ds_commit_program import Ui_DSCommitProgram

from dsviper import (
    CommitStore,
    ValueCommitId,
    CommitHeader,
    ValueOpcodeDocumentSet,
    ValueOpcodeDocumentUpdate,
    ValueOpcodeSetUnion,
    ValueOpcodeSetSubtract,
    ValueOpcodeMapUnion,
    ValueOpcodeMapSubtract,
    ValueOpcodeMapUpdate,
    ValueOpcodeXArrayInsert,
    ValueOpcodeXArrayRemove,
    ValueOpcodeXArrayUpdate
)

from dsviper import Html, ValueOpcode
from .ds_commit_store_notifier import DSCommitStoreNotifier


class DSCommitProgram(QFrame, Ui_DSCommitProgram):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)

        self._store: CommitStore | None = None
        self._opcodes: list[ValueOpcode] = []
        self._setup_connections()

    def set_store(self, store: CommitStore):
        self._store = store

    def _setup_connections(self):
        notifier = DSCommitStoreNotifier.instance()
        notifier.database_did_open.connect(self._store_database_did_open)
        notifier.database_did_close.connect(self._store_database_did_close)
        notifier.state_did_change.connect(self._store_state_did_change)

        self.w_tree_widget.itemSelectionChanged.connect(self._tree_selection_changed)
        self.w_use_commit_state_trace_button.clicked.connect(self._use_eval_action_clicked)
        self.w_use_description_button.clicked.connect(self._use_description_clicked)

        self.w_commit_id_copy_button.clicked.connect(self._commit_id_copy_clicked)
        self.w_parent_id_copy_button.clicked.connect(self._parent_id_copy_clicked)
        self.w_target_id_copy_button.clicked.connect(self._target_id_copy_clicked)

    def _store_database_did_open(self):
        self._clear()
        self._configure()

    def _store_database_did_close(self):
        self._clear()
        self._configure()

    def _store_state_did_change(self):
        self._configure()

    def _tree_selection_changed(self):
        self._show_selected_row()

    def _use_eval_action_clicked(self):
        self._configure()

    def _use_description_clicked(self):
        self._show_selected_row()

    def _commit_id_copy_clicked(self):
        self._copy_identifier(self.w_commit_id_label)

    def _parent_id_copy_clicked(self):
        self._copy_identifier(self.w_parent_id_label)

    def _target_id_copy_clicked(self):
        self._copy_identifier(self.w_target_id_label)

    def _copy_identifier(self, label: QLabel):
        QGuiApplication.clipboard().setText(label.text())

    def _clear(self):
        self._opcodes = []
        self._clear_value()

    def _configure(self):
        if not self._store.has_database():
            self._clear_header()
            self._reload_data()
            return

        db = self._store.database()

        commit_id = self._store.state().commit_id()
        if not commit_id.is_valid():
            return

        commit = db.commit(commit_id)
        self._opcodes.clear()
        if self.w_use_commit_state_trace_button.isChecked():
            self._opcodes = self._store.state().traced_opcodes()
        else:
            if commit.program():
                self._opcodes = commit.program().all_opcodes()

        self._configure_header(commit.header())
        self._reload_data()

    def _repr_commit_id(self, commit_id: ValueCommitId):
        return commit_id.encoded() if commit_id.is_valid() else ""

    def _configure_header(self, header: CommitHeader):
        self.w_label_label.setText(header.label())
        timestamp = QDateTime.fromSecsSinceEpoch(int(header.timestamp()))
        self.w_date_label.setText(timestamp.toString())

        self.w_type_label.setText(str(header.commit_type()))
        self.w_target_id_label.setText(self._repr_commit_id(header.target_commit_id()))
        self.w_commit_id_label.setText(self._repr_commit_id(header.commit_id()))
        self.w_parent_id_label.setText(self._repr_commit_id(header.parent_commit_id()))

    def _clear_header(self):
        na = "-"
        self.w_label_label.clear()
        self.w_date_label.setText(na)
        self.w_type_label.setText(na)
        self.w_target_id_label.setText(na)
        self.w_commit_id_label.setText(na)
        self.w_parent_id_label.setText(na)

    def _reload_data(self):
        self.w_tree_widget.blockSignals(True)
        self.w_tree_widget.clear()
        self.w_tree_widget.blockSignals(False)

        if not self._store.has_database():
            return

        self.w_tree_widget.blockSignals(True)
        definitions = self._store.database().definitions()
        first_item: QTreeWidgetItem | None = None

        for opcode in self._opcodes:
            str_opcode_type = opcode.type()
            opcode_key = opcode.key()
            attachment = definitions.check_attachment(opcode_key.attachment_runtime_id())
            str_attachment = attachment.type_name().name()
            str_concept = definitions.check_concept(opcode_key.concept_runtime_id()).representation()
            str_instance_id = opcode_key.instance_id().encoded()
            str_path = "-"

            if isinstance(opcode, ValueOpcodeDocumentUpdate):
                str_path = opcode.path().representation()
            elif isinstance(opcode, ValueOpcodeSetUnion):
                str_path = opcode.path().representation()
            elif isinstance(opcode, ValueOpcodeSetSubtract):
                str_path = opcode.path().representation()
            elif isinstance(opcode, ValueOpcodeMapUnion):
                str_path = opcode.path().representation()
            elif isinstance(opcode, ValueOpcodeMapSubtract):
                str_path = opcode.path().representation()
            elif isinstance(opcode, ValueOpcodeMapUpdate):
                str_path = opcode.path().representation()
            elif isinstance(opcode, ValueOpcodeXArrayInsert):
                str_path = opcode.path().representation()
            elif isinstance(opcode, ValueOpcodeXArrayRemove):
                str_path = opcode.path().representation()
            elif isinstance(opcode, ValueOpcodeXArrayUpdate):
                str_path = opcode.path().representation()

            str_position = "-"
            if isinstance(opcode, ValueOpcodeXArrayInsert):
                str_position = opcode.position().encoded()
            elif isinstance(opcode, ValueOpcodeXArrayRemove):
                str_position = opcode.position().encoded()
            elif isinstance(opcode, ValueOpcodeXArrayUpdate):
                str_position = opcode.position().encoded()

            str_before_position = "-"
            if isinstance(opcode, ValueOpcodeXArrayInsert):
                str_before_position = opcode.before_position().encoded()

            texts = [str_attachment, str_concept, str_instance_id, str_opcode_type, str_path, str_position,
                     str_before_position]

            item = QTreeWidgetItem(self.w_tree_widget, texts)
            item.setToolTip(1, attachment.representation())

            if first_item is None:
                first_item = item

        self.w_tree_widget.blockSignals(False)

        if first_item:
            self.w_tree_widget.setCurrentItem(first_item)
        else:
            self._clear_value()

    def _show_selected_row(self):
        selected_row = self.w_tree_widget.currentIndex().row()
        if selected_row == -1:
            self._clear_value()
            return

        opcode = self._opcodes[selected_row]

        value = None
        if isinstance(opcode, ValueOpcodeDocumentSet):
            value = opcode.value()
        elif isinstance(opcode, ValueOpcodeDocumentUpdate):
            value = opcode.value()
        elif isinstance(opcode, ValueOpcodeSetUnion):
            value = opcode.value()
        elif isinstance(opcode, ValueOpcodeSetSubtract):
            value = opcode.value()
        elif isinstance(opcode, ValueOpcodeMapUnion):
            value = opcode.value()
        elif isinstance(opcode, ValueOpcodeMapSubtract):
            value = opcode.value()
        elif isinstance(opcode, ValueOpcodeMapUpdate):
            value = opcode.value()
        elif isinstance(opcode, ValueOpcodeSetSubtract):
            value = opcode.value()
        elif isinstance(opcode, ValueOpcodeXArrayUpdate):
            value = opcode.value()

        if value:
            use_description = self.w_use_description_button.isChecked()
            content = Html.value(value, use_description=use_description)
            self._set_value(content)
        else:
            self._clear_value()

    def _clear_value(self):
        self._set_value("")

    def _set_value(self, content: str):
        document = Html.document("Value Representation", Html.style(), Html.body(content))
        self.w_text_edit.setHtml(document)
