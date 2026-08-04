"""The edits the installer makes to the user's files, as pure transforms.

Every function here takes and returns data rather than touching the disk, so the
installer's effect on a real HOI4 install is testable without one.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence

# Files the release zip must contain for an install to be possible.
REQUIRED_DIST_FILES = (
    "checkupdate.exe",
    "hoi4Presence.exe",
    "version.json",
    "runRPC.bat",
    "runRPC.exe",
)

# The launcher's exePath/exeArgs before and after installation. The Paradox
# launcher spawns its target without a shell and cannot run a .bat directly,
# hence the runRPC.exe shim.
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


def rewriteBatchDocumentsPath(lines: Sequence[str], documentsPath: str) -> list[str]:
    """Replace the ``documentsPath`` assignment on the first line of runRPC.bat."""
    rewritten = list(lines)
    if not rewritten:
        raise ValueError("runRPC.bat is empty")
    rewritten[0] = f'set "documentsPath={documentsPath}"\n'
    return rewritten
