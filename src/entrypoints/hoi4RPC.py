"""Entry point for hoi4Presence.exe -- the Discord Rich Presence itself."""

from __future__ import annotations

import sys
from pathlib import Path

if not getattr(sys, "frozen", False):
    # Running from source: make src/ importable so `python src/entrypoints/hoi4RPC.py`
    # works without setting PYTHONPATH. PyInstaller bundles the package instead.
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from hoi4presence.logging_setup import setupLogging
from hoi4presence.paths import getBaseDir, getSavePath
from hoi4presence.runner import run


def main() -> int:
    baseDir = getBaseDir(__file__)
    setupLogging(baseDir)
    return run(getSavePath(baseDir))


if __name__ == "__main__":
    sys.exit(main())
