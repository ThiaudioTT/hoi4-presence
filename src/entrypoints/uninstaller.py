"""Entry point for uninstall.exe -- reverses everything setup.exe did."""

from __future__ import annotations

import sys
from pathlib import Path

if not getattr(sys, "frozen", False):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import json
import shutil

from hoi4presence.install.steps import (
    CONFIG_NAME,
    LAUNCHER_SETTINGS,
    LEGACY_BATCH_NAME,
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
from hoi4presence.ui import Wizard

TOTAL_STEPS = 5


def main() -> int:
    with Wizard(
        "hoi4-presence uninstall",
        "Removes the Discord Rich Presence from your Hearts of Iron IV install.",
        totalSteps=TOTAL_STEPS,
    ) as wizard:
        with wizard.step("Locating the HOI4 documents folder"):
            documents = findDocumentsDir(defaultDocumentsDir(), wizard.ask, wizard.warn)

        # Restore binary saves, which the installer turned off.
        try:
            with wizard.step(f"Restoring save_as_binary=yes in {SETTINGS_FILE}"):
                settingsPath = documents / SETTINGS_FILE
                settings = settingsPath.read_text(encoding="utf-8")
                settingsPath.write_text(setBinarySaves(settings, enabled=True), encoding="utf-8")
        except (OSError, ValueError) as error:
            return wizard.fail(f"{error}\n\nCan't revert {SETTINGS_FILE}")

        with wizard.step("Locating the game folder"):
            gameFolder = findGameDir(defaultGameDir(), wizard.ask, wizard.warn)

        # Point the Paradox launcher back at the game itself.
        try:
            with wizard.step(f"Pointing {LAUNCHER_SETTINGS} back at the game"):
                launcherPath = gameFolder / LAUNCHER_SETTINGS
                launcher = json.loads(launcherPath.read_text(encoding="utf-8"))
                launcherPath.write_text(
                    json.dumps(setLauncherExe(launcher, install=False), indent=4),
                    encoding="utf-8",
                )
        except (OSError, ValueError) as error:
            return wizard.fail(f"{error}\n\nCan't revert {LAUNCHER_SETTINGS}")

        try:
            with wizard.step("Deleting the rich presence"):
                # ignore_errors so a second run, or one after the folder was deleted by
                # hand, still clears the files left in the game folder below.
                shutil.rmtree(documents / INSTALL_DIR_NAME, ignore_errors=True)
                (gameFolder / SHIM_NAME).unlink(missing_ok=True)
                (gameFolder / CONFIG_NAME).unlink(missing_ok=True)
                # Left behind by a 1.3.x install this one was upgraded from.
                (gameFolder / LEGACY_BATCH_NAME).unlink(missing_ok=True)
        except OSError as error:
            return wizard.fail(f"{error}\n\nCould not delete rich presence")

        wizard.finish(
            "hoi4-presence has been uninstalled.",
            "Your saves are untouched, and the Paradox launcher starts the game directly again.",
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
