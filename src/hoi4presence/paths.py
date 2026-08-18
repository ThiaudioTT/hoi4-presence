"""Filesystem discovery shared by the presence, the updater and the installer.

Nothing here touches ``os.environ`` or the disk at import time: the Windows
defaults are exposed as functions taking an explicit environment, so this module
imports cleanly on Linux CI where ``USERPROFILE`` does not exist.
"""

from __future__ import annotations

import glob
import os
import sys
from collections.abc import Callable, Mapping
from pathlib import Path

# Where HOI4 keeps its saves and settings, relative to the user's profile.
DOCUMENTS_SUBPATH = Path("Documents") / "Paradox Interactive" / "Hearts of Iron IV"
# Where Steam installs the game, relative to Program Files (x86).
GAME_SUBPATH = Path("Steam") / "steamapps" / "common" / "Hearts of Iron IV"

SAVE_DIR_NAME = "save games"
SAVE_GLOB = "*.hoi4"

# Marker files used to recognise each directory.
SETTINGS_FILE = "settings.txt"
GAME_EXE = "hoi4.exe"

# Name of the folder the installer creates inside the documents directory.
INSTALL_DIR_NAME = "hoi4Presence"


def getBaseDir(scriptPath: str | os.PathLike[str] | None = None) -> Path:
    """Return the directory the running program should treat as its own.

    Frozen by PyInstaller, that is the folder holding the executable. Running
    from source it is the folder holding the entry-point script, so callers pass
    their own ``__file__``.
    """
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    if scriptPath is not None:
        return Path(scriptPath).resolve().parent
    return Path(sys.argv[0]).resolve().parent


def getSavePath(baseDir: str | os.PathLike[str]) -> str:
    """Return the glob matching HOI4 saves, as a sibling of ``baseDir``.

    Installed, the presence lives in ``<documents>/hoi4Presence`` and the saves
    in ``<documents>/save games``. Running from source, the entry point lives in
    ``src/entrypoints`` and the sample saves in ``src/save games``. The same
    ``../save games`` hop covers both.

    Only ``SAVE_GLOB`` is left as a pattern: a documents folder containing
    brackets, such as ``D:\\Games [SSD]``, would otherwise be read as a glob
    character class and match no save at all.
    """
    saveDir = os.path.abspath(os.path.join(baseDir, "..", SAVE_DIR_NAME))
    return os.path.join(glob.escape(saveDir), SAVE_GLOB)


def defaultDocumentsDir(env: Mapping[str, str] | None = None) -> Path:
    """Default HOI4 documents directory. Windows-only; raises KeyError elsewhere."""
    env = os.environ if env is None else env
    return Path(env["USERPROFILE"]) / DOCUMENTS_SUBPATH


def defaultGameDir(env: Mapping[str, str] | None = None) -> Path:
    """Default Steam install directory. Windows-only; raises KeyError elsewhere."""
    env = os.environ if env is None else env
    return Path(env["PROGRAMFILES(X86)"]) / GAME_SUBPATH


def findDirContaining(
    start: str | os.PathLike[str],
    marker: str,
    missingDirLabel: str,
    prompt: Callable[[str], str],
    log: Callable[[str], None] | None = None,
) -> Path:
    """Return a directory containing ``marker``, asking the user until one does.

    ``prompt`` is called with the question and must return a path; ``log``, if
    given, receives the reason the previous candidate was rejected. Both are
    injected so tests can drive the retry loop without stdin.
    """
    current = Path(start)
    while True:
        if current.is_dir():
            if (current / marker).exists():
                return current
            reason = f"Could not find {marker!r} in {str(current)!r}"
            label = repr(marker)
        else:
            reason = f"Could not find directory {str(current)!r}"
            label = missingDirLabel

        if log is not None:
            log(reason)
        # Explorer's "Copy as path" wraps the path in quotes, which would never
        # resolve and would leave the user re-prompted forever.
        answer = prompt(f"Can't find {label}, please enter the path manually: ")
        current = Path(answer.strip().strip('"'))


def findDocumentsDir(
    start: str | os.PathLike[str],
    prompt: Callable[[str], str],
    log: Callable[[str], None] | None = None,
) -> Path:
    """Locate the HOI4 documents directory, recognised by ``settings.txt``."""
    return findDirContaining(start, SETTINGS_FILE, "documents path", prompt, log)


def findGameDir(
    start: str | os.PathLike[str],
    prompt: Callable[[str], str],
    log: Callable[[str], None] | None = None,
) -> Path:
    """Locate the HOI4 install directory, recognised by ``hoi4.exe``."""
    return findDirContaining(start, GAME_EXE, "game folder path", prompt, log)
