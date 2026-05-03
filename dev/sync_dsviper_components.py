#!/usr/bin/env python3
# Maintainer-only — sync dsviper_components/ source files from the
# external dsviper-components repository.
# Excluded from dsviper-X.Y.Z-devkit.zip via the `dev/` filter.
#
# Run from the repo root after pulling updates in the sibling repo:
#
#     python3 dev/sync_dsviper_components.py
#     python3 dev/build.py             # regenerate ui_*.py and resources_rc.py
#     git add dsviper_components resources_rc.py
#     git commit -m "sync: bump dsviper-components to vX.Y.Z"
#
# This script DOES NOT regenerate ui_*.py or resources_rc.py — that
# is dev/build.py's job. Keep the steps separate so a contributor
# editing only a local *.ui file (without touching the sibling) does
# not need to run sync.
#
# Source resolution (in order):
#   1. $DSVIPER_COMPONENTS — explicit path to a dsviper-components checkout
#   2. ../dsviper-components — sibling-checkout (dev)
#   3. installed wheel `dsviper_components` — future PyPI consumption
#
# What gets copied:
#   - *.py (component logic — excludes ui_*.py)
#   - *.ui (Qt Designer XML)
#   - images/ (PNG icons)
#
# What does NOT get copied:
#   - resources.qrc — this repo uses its own root resources.qrc
#     which lists both component icons and app-specific icons
#     (cdbe_icon, dbe_icon)
#   - ui_*.py and resources_rc.py — regenerated locally by dev/build.py
#   - __pycache__/ and bytecode

from __future__ import annotations

import importlib.util
import os
import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PKG = REPO / "dsviper_components"


def resolve_source() -> Path:
    """Resolve the dsviper-components source directory.

    Returns the path to the `dsviper_components/` package directory
    inside the source repo or installed wheel.
    """
    # 1. Explicit override
    if env := os.environ.get("DSVIPER_COMPONENTS"):
        candidate = Path(env)
        for c in (candidate / "dsviper_components", candidate):
            if (c / "__init__.py").is_file():
                return c
        sys.exit(
            f"error: $DSVIPER_COMPONENTS={env} does not contain a "
            f"dsviper_components package"
        )

    # 2. Sibling-checkout
    sibling = REPO.parent / "dsviper-components" / "dsviper_components"
    if (sibling / "__init__.py").is_file():
        return sibling

    # 3. Installed wheel
    spec = importlib.util.find_spec("dsviper_components")
    if spec is not None and spec.origin:
        return Path(spec.origin).resolve().parent

    sys.exit(
        "error: cannot resolve dsviper-components source. "
        "Either checkout dsviper-components alongside this repo "
        "(github.com/digital-substrate/dsviper-components), set "
        "$DSVIPER_COMPONENTS, or pip install dsviper-components."
    )


def sync(src: Path) -> None:
    """Wipe and re-populate PKG from `src` (a dsviper_components/ dir)."""
    if PKG.exists():
        shutil.rmtree(PKG)

    def ignore(_dir: str, names: list[str]) -> list[str]:
        del _dir
        return [
            n for n in names
            if n == "__pycache__"
            or n == "resources.qrc"
            or n == "resources_rc.py"
            or (n.startswith("ui_") and n.endswith(".py"))
        ]

    shutil.copytree(src, PKG, ignore=ignore)


def main() -> None:
    src = resolve_source()
    print(f"Source: {src}")
    print(f"Target: {PKG.relative_to(REPO)}/")
    sync(src)
    n_py = sum(1 for _ in PKG.glob("*.py"))
    n_ui = sum(1 for _ in PKG.glob("*.ui"))
    n_img = sum(1 for _ in (PKG / "images").iterdir()) if (PKG / "images").is_dir() else 0
    print(f"Synced: {n_py} *.py, {n_ui} *.ui, {n_img} images.")
    print()
    print("Next: run `python3 dev/build.py` to regenerate ui_*.py and resources_rc.py.")


if __name__ == "__main__":
    main()
