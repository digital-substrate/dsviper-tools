from __future__ import annotations
from dsviper import *


def inspect_selection():
    """Return (key, attachment, path) of the current document selection."""
    sel = _documents_panel.selection()
    if sel:
        return sel.key, sel.attachment, sel.path
    return None, None, None

print("** CDBEditor: Hello from main_init.py **")
print("")
