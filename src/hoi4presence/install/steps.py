"""The edits the installer makes to the user's files, as pure transforms.

Every function here takes and returns data rather than touching the disk, so the
installer's effect on a real HOI4 install is testable without one.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence

# The files the installer moves around, by name. These are load-bearing:
# build.spec and launcher.py refer to the same strings. Rename the source script
# if you must; never rename the exe. See AGENTS.md.
#
# `launcher.py` repeats these rather than importing them: the shim is the first
# link in the launch chain and is deliberately stdlib-only.
SHIM_NAME = "runRPC.exe"
UPDATER_EXE = "checkupdate.exe"
PRESENCE_EXE = "hoi4Presence.exe"
LAUNCHER_SETTINGS = "launcher-settings.json"

# Written into the game folder at install time, holding the documents path the
# installer resolved -- the one thing the shim cannot work out for itself.
CONFIG_NAME = "runRPC.cfg"

# Up to 1.3.x the shim ran a batch file that carried that path instead. Old
# installs still have a copy sitting in the game folder; setup and uninstall
# clear it. Drop this once nobody is upgrading from 1.3.x any more.
LEGACY_BATCH_NAME = "runRPC.bat"

# Files the release zip must contain for an install to be possible. CONFIG_NAME
# is not among them: the installer writes it, the build does not ship it.
REQUIRED_DIST_FILES = (
    UPDATER_EXE,
    PRESENCE_EXE,
    "version.json",
    SHIM_NAME,
)

# The launcher's exePath/exeArgs before and after installation. The Paradox
# launcher spawns its target with its own arguments prepended, so the shim
# re-launches the game with the argument order we control.
PRESENCE_LAUNCHER = ("./runRPC.exe", [])
VANILLA_LAUNCHER = ("./hoi4.exe", ["-gdpr-compliant"])

BINARY_SAVES_ON = "save_as_binary=yes"
BINARY_SAVES_OFF = "save_as_binary=no"

UPDATE_FLAG = "-update"


def isUpdateMode(argv: Sequence[str]) -> bool:
    """Whether the installer was launched by the auto-updater."""
    return len(argv) >= 2 and argv[1] == UPDATE_FLAG


def findMissingFiles(present: Iterable[str], required: Iterable[str] = REQUIRED_DIST_FILES) -> list[str]:
    """Return the required files that are absent from ``present``.

    The original check did the opposite -- it collected files that were present
    but *not* required, so a genuinely missing executable passed silently while
    any extra file in the folder aborted the install.
    """
    have = set(present)
    return [name for name in required if name not in have]


def setBinarySaves(settingsText: str, *, enabled: bool) -> str:
    """Toggle HOI4's ``save_as_binary`` setting.

    The presence can only read plaintext saves, so installing turns this off and
    uninstalling restores it. Idempotent in both directions.
    """
    if enabled:
        return settingsText.replace(BINARY_SAVES_OFF, BINARY_SAVES_ON)
    return settingsText.replace(BINARY_SAVES_ON, BINARY_SAVES_OFF)


def setLauncherExe(launcher: dict, *, install: bool) -> dict:
    """Point ``launcher-settings.json`` at the presence shim, or back at the game.

    Returns a copy so unrelated keys in the user's launcher config are preserved
    exactly.
    """
    exePath, exeArgs = PRESENCE_LAUNCHER if install else VANILLA_LAUNCHER
    updated = dict(launcher)
    updated["exePath"] = exePath
    updated["exeArgs"] = list(exeArgs)
    return updated
