#!/usr/bin/env python
from __future__ import annotations

from pathlib import Path

from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QMessageBox,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

VERSION = "1.2"
COPYRIGHT = "Copyright (c) 2026 Digital Substrate"
LICENSE_ID = "MIT"


def get_license_path() -> Path:
    dsviper_components_dir = Path(__file__).parent
    tools_dir = dsviper_components_dir.parent
    return tools_dir / "LICENSE"


def get_license_text() -> str:
    license_path = get_license_path()
    if license_path.exists():
        return license_path.read_text(encoding="utf-8")
    return "License file not found."


class DSLicenseDialog(QDialog):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setWindowTitle("License")
        self.resize(640, 480)

        layout = QVBoxLayout(self)

        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setFont(QFont("monospace", 10))
        text_edit.setPlainText(get_license_text())
        layout.addWidget(text_edit)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)


def show_license_dialog(parent: QWidget | None = None) -> None:
    dialog = DSLicenseDialog(parent)
    dialog.exec()


def show_about_dialog(parent: QWidget, app_name: str, app_description: str) -> None:
    msg = QMessageBox(parent)
    msg.setWindowTitle(f"About {app_name}")
    msg.setIcon(QMessageBox.Icon.Information)
    msg.setText(f"<b>{app_name}</b> v{VERSION}")
    msg.setInformativeText(
        f"{app_description}\n\n"
        f"{COPYRIGHT}\n"
        f"Licensed under {LICENSE_ID}"
    )

    license_button = msg.addButton("License...", QMessageBox.ButtonRole.ActionRole)
    msg.addButton(QMessageBox.StandardButton.Ok)

    msg.exec()

    if msg.clickedButton() == license_button:
        show_license_dialog(parent)
