#!/usr/bin/env python3
# Canonical build entry point — regenerates ui_*.py and resources_rc.py
# from .ui/.qrc sources. Not shipped in the published DevKit ZIP.
#
# Run from the repo root:
#
#     python3 dev/build.py
#
# Inputs and outputs both live in this repo:
#   - inputs : dsviper_components/*.ui, resources.qrc
#   - outputs: dsviper_components/ui_*.py, resources_rc.py
#
# Idempotent: running twice on a clean tree leaves the tree clean.
# Success criterion: `git status` is clean both before and after.
#
# The PySide6 version is pinned in requirements.txt; mismatches between
# contributors silently produce different generated files (phantom diffs).

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
QRC = REPO / "resources.qrc"
RCC_OUT = REPO / "resources_rc.py"
UI_DIR = REPO / "dsviper_components"


def require(tool: str) -> str:
    path = shutil.which(tool)
    if not path:
        sys.exit(f"error: {tool} not found in PATH (install PySide6).")
    return path


def pyside6_version() -> str:
    try:
        import PySide6
    except ImportError:
        sys.exit("error: PySide6 not installed (pip install -r requirements.txt).")
    return PySide6.__version__


def regen_resources(rcc: str) -> None:
    if not QRC.is_file():
        sys.exit(f"error: missing {QRC.relative_to(REPO)}")
    print(f"  pyside6-rcc {QRC.name} -> {RCC_OUT.name}")
    subprocess.run([rcc, str(QRC), "-o", str(RCC_OUT)], check=True, cwd=REPO)


def regen_ui(uic: str) -> None:
    ui_files = sorted(UI_DIR.glob("*.ui"))
    if not ui_files:
        sys.exit(f"error: no *.ui files in {UI_DIR.relative_to(REPO)}")
    for ui in ui_files:
        out = ui.with_name(f"ui_{ui.stem}.py")
        print(f"  pyside6-uic {ui.relative_to(REPO)} -> {out.relative_to(REPO)}")
        subprocess.run([uic, str(ui), "-o", str(out)], check=True, cwd=REPO)


def main() -> None:
    print(f"PySide6 {pyside6_version()}")
    rcc = require("pyside6-rcc")
    uic = require("pyside6-uic")
    print("Regenerating Qt resource module...")
    regen_resources(rcc)
    print("Regenerating UI modules...")
    regen_ui(uic)
    print("Done.")


if __name__ == "__main__":
    main()
