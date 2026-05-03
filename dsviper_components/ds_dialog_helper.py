from __future__ import annotations

from PySide6.QtCore import QRect
from PySide6.QtWidgets import QDialog


def toggle(dialog: QDialog, geometry: QRect):
    if dialog.isVisible():
        hide(dialog, geometry)
    else:
        show(dialog, geometry)


def show(dialog: QDialog, geometry: QRect):
    dialog.show()
    if geometry.width() != 0:
        dialog.setGeometry(geometry)


def hide(dialog: QDialog, geometry: QRect):
    g = dialog.geometry()
    geometry.setRect(g.x(), g.y(), g.width(), g.height())
    dialog.hide()
