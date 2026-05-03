from PySide6.QtWidgets import QDialog
from .ui_ds_database_select_dialog import Ui_Dialog

class DSDatabaseSelectDialog(QDialog, Ui_Dialog):

    def __init__(self, databases: list[str], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)
        self.w_databases_list_widget.addItems(databases)

        self.w_cancel_button.clicked.connect(self.reject)
        self.w_ok_button.clicked.connect(self._accept)

    def _accept(self):
        self.accept()

    def selected(self) -> str | None:
        items = self.w_databases_list_widget.selectedItems()
        if items:
            return items[0].text()
        return None