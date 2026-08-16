"""Entry point for uninstall.exe -- reverses everything setup.exe did."""

from __future__ import annotations

import sys
from pathlib import Path

if not getattr(sys, "frozen", False):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import json
import shutil
import time

from hoi4presence.install.steps import (
    BATCH_NAME,
    LAUNCHER_SETTINGS,
    SHIM_NAME,
    setBinarySaves,
    setLauncherExe,
)
from hoi4presence.paths import (
    INSTALL_DIR_NAME,
    SETTINGS_FILE,
    defaultDocumentsDir,
    defaultGameDir,
    findDocumentsDir,
    findGameDir,
)


def fail(message: str, *, delay: int = 3) -> int:
    print(f"\n{message}\n\nExiting...")
    time.sleep(delay)
    return 1


def main() -> int:
    print("This script will uninstall the hoi4-presence in your game/save path\nPress enter to continue...")
    input()

    documents = findDocumentsDir(defaultDocumentsDir(), input, print)
    print("Documents directory found")

    # Restore binary saves, which the installer turned off.
    try:
        settingsPath = documents / SETTINGS_FILE
        print(f"Writing save_as_binary=yes in {SETTINGS_FILE}...")
        settings = settingsPath.read_text(encoding="utf-8")
        settingsPath.write_text(setBinarySaves(settings, enabled=True), encoding="utf-8")
    except (OSError, ValueError) as error:
        return fail(f"{error}\nCan't revert {SETTINGS_FILE}")

    gameFolder = findGameDir(defaultGameDir(), input, print)
    print("Game directory found")

    # Point the Paradox launcher back at the game itself.
    try:
        print(f"Changing {LAUNCHER_SETTINGS}...")
        launcherPath = gameFolder / LAUNCHER_SETTINGS
        launcher = json.loads(launcherPath.read_text(encoding="utf-8"))
        launcherPath.write_text(
            json.dumps(setLauncherExe(launcher, install=False), indent=4),
            encoding="utf-8",
        )
    except (OSError, ValueError) as error:
        return fail(f"{error}\nCan't revert {LAUNCHER_SETTINGS}")

    try:
        print("Deleting rich presence")
        # ignore_errors so a second run, or one after the folder was deleted by
        # hand, still clears the two files left in the game folder below.
        shutil.rmtree(documents / INSTALL_DIR_NAME, ignore_errors=True)
        (gameFolder / BATCH_NAME).unlink(missing_ok=True)
        (gameFolder / SHIM_NAME).unlink(missing_ok=True)
    except OSError as error:
        return fail(f"{error}\nCould not delete rich presence")

    print("Uninstalled!\nPress 'Enter' or close this window.")
    time.sleep(4)
    input()
    return 0


if __name__ == "__main__":
    sys.exit(main())
