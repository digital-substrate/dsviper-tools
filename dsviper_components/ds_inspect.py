from __future__ import annotations

from PySide6.QtWidgets import QFrame

from .ui_ds_inspect import Ui_DSInspect
from dsviper import DSMDefinitions, DSMAttachment, DefinitionsConst, Html, ViperError

class DSInspect(QFrame, Ui_DSInspect):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)
        self._store = None
        self._show_all = False
        self._dsm_definitions: DSMDefinitions | None = None
        self._selected_attachments: list[DSMAttachment] = []
        self._attachments: list[DSMAttachment] = []

        self._setup_connections()
        self._configure_dsm_buttons(False)

    def set_path(self, value: str):
        self.w_path_label.setText(value)

    def set_documentation(self, value: str):
        self.w_documentation_label.setText(value)

    def set_uuid(self, value: str):
        self.w_uuid_label.setText(value)

    def set_codec_name(self, value: str):
        self.w_codec_label.setText(value)

    def set_definition_hexdigest(self, value: str):
        self.w_definitions_hexdigest_label.setText(value)

    def set_definitions(self, definitions: DefinitionsConst):
        self._configure(definitions)

    def clear(self):
        self._clear_information()
        self._clear_summary()
        self._clear_dsm()

    def _setup_connections(self):
        self.w_show_documentation_check_box.clicked.connect(self._show_documentation_clicked)
        self.w_show_runtime_id_check_box.clicked.connect(self._show_attribute_clicked)
        self.w_attachment_combo_box.lineEdit().returnPressed.connect(self._attachment_return_pressed)
        self.w_attachment_combo_box.currentTextChanged.connect(self._attachment_current_index_changed)

    def _store_database_did_open(self):
        self.clear()
        self._configure(self._store.database())

    def _store_database_did_close(self):
        self.clear()

    def _store_definitions_did_change(self):
        self.clear()
        self._configure(self._store.database())

    def _show_attribute_clicked(self):
        self._configure_dsm_view()

    def _show_documentation_clicked(self):
        self._configure_dsm_view()

    def _attachment_return_pressed(self):
        self._render_dsm()

    def _attachment_current_index_changed(self):
        self._render_dsm()

    def _configure(self, definitions: DefinitionsConst):
        try:
            self._configure_summary(definitions)

            self._dsm_definitions = definitions.to_dsm_definitions()
            self._configure_dsm_attachments()

            if len(self._attachments):
                self._selected_attachments = [self._attachments[0]]

            self._configure_dsm_view()
            self._configure_dsm_buttons(True)

        except ViperError as e:
            self._except_present(e)

    def _clear_information(self):
        self.w_path_label.clear()
        self.w_documentation_label.clear()
        self.w_uuid_label.clear()
        self.w_codec_label.clear()
        self.w_definitions_hexdigest_label.clear()

    def _pluralize_definition(self, definition: str, count: int):
        result = f'{count} {definition}'
        if count > 1:
            result += "s"
        return result

    def _clear_summary(self):
        self.w_concepts_label.clear()
        self.w_clubs_label.clear()
        self.w_enumerations_label.clear()
        self.w_structures_label.clear()
        self.w_attachments_label.clear()

    def _configure_summary(self, definitions: DefinitionsConst):
        self.w_concepts_label.setText(self._pluralize_definition("concept", len(definitions.concepts())))
        self.w_clubs_label.setText(self._pluralize_definition("club", len(definitions.clubs())))
        self.w_enumerations_label.setText(self._pluralize_definition("enumeration", len(definitions.enumerations())))
        self.w_structures_label.setText(self._pluralize_definition("structure", len(definitions.structures())))
        self.w_attachments_label.setText(self._pluralize_definition("attachment", len(definitions.attachments())))

    def _configure_dsm_view(self):
        attachments: list[DSMAttachment]  = []
        if not self._show_all:
            attachments = self._selected_attachments
            
        show_documentation = self.w_show_documentation_check_box.isChecked()
        show_runtime_id = self.w_show_runtime_id_check_box.isChecked()
        content = self._dsm_definitions.to_dsm(show_documentation=show_documentation,
                                               show_runtime_id=show_runtime_id,
                                               html=True,
                                               attachments=attachments)


        style = Html.style()
        body = Html.body(content)
        document = Html.document("DSM Definitions", style, body)

        self.w_dsm_textedit.setHtml(document)

    def _configure_dsm_buttons(self, enabled: bool):
        self.w_show_documentation_check_box.setEnabled(enabled)
        self.w_show_runtime_id_check_box.setEnabled(enabled)
        self.w_attachment_combo_box.setEnabled(enabled)

    def _configure_dsm_attachments(self):
        self._attachments = self._dsm_definitions.attachments()
        self._attachments.sort(key=lambda a: a.identifier())

        self.w_attachment_combo_box.blockSignals(True)
        self.w_attachment_combo_box.clear()

        for attachment in self._attachments:
            self.w_attachment_combo_box.addItem(attachment.identifier())

        self.w_attachment_combo_box.blockSignals(False)
        self._selected_attachments = self._attachments

    def _render_dsm(self):
        self._show_all = False
        text = self.w_attachment_combo_box.lineEdit().text()

        if len(text) == 0:
            self._selected_attachments = self._attachments
            self._show_all = True
        else:
            selected_index: int | None = None
            for i, attachment in enumerate(self._attachments):
                sr = attachment.identifier()
                if sr == text:
                    selected_index = i
                    break

            if selected_index:
                self._selected_attachments = [self._attachments[selected_index]]
            else:
                candidates: list[DSMAttachment] = []
                for attachment in self._dsm_definitions.attachments():
                    sr = attachment.identifier()
                    if sr.find(text) != -1:
                        candidates.append(attachment)

                if len(candidates):
                    self._selected_attachments = candidates

        self._configure_dsm_view()

    def _clear_dsm(self):
        self._selected_attachments.clear()
        self._attachments.clear()

        self.w_show_documentation_check_box.setChecked(False)
        self.w_show_documentation_check_box.setEnabled(False)
        self.w_show_runtime_id_check_box.setChecked(False)
        self.w_show_runtime_id_check_box.setEnabled(False)
        self.w_attachment_combo_box.clear()
        self.w_attachment_combo_box.setEnabled(False)
        self.w_dsm_textedit.clear()

    def _except_present(self, e):
        print(e)