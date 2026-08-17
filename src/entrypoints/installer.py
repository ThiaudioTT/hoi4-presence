"""Entry point for setup.exe -- installs the presence into a HOI4 install.

This is a console wizard, so it talks to the user through
:class:`hoi4presence.ui.Wizard` rather than the logger; the windowed executables
are the ones that need a log file.

What it does, in order:

1. verify the unpacked release contains everything it needs;
2. stop a running presence (auto-update only);
3. locate the HOI4 documents folder and copy the payload into it;
4. turn off binary saves, so the presence can read them;
5. locate the game folder, drop the launcher shim in and write the documents
   path beside it as runRPC.cfg, which is how the shim finds the payload;
6. point launcher-settings.json at that shim.
"""

from __future__ import annotations

import sys
from pathlib import Path

if not getattr(sys, "frozen", False):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import json
import os
import shutil
import subprocess
import time

from hoi4presence.install.steps import (
    CONFIG_NAME,
    LAUNCHER_SETTINGS,
    LEGACY_BATCH_NAME,
    PRESENCE_EXE,
    REQUIRED_DIST_FILES,
    SHIM_NAME,
    findMissingFiles,
    isUpdateMode,
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
    getBaseDir,
)
from hoi4presence.ui import Wizard

SOURCE_SUBPATH = Path("discordRPC") / "dist"

# Every stage below, plus "stop the running presence" on the auto-update path.
BASE_STEPS = 7

# Windows frees a deleted directory lazily, so copytree can still trip over the
# one we just removed. Nothing to do with the wizard's pacing, which is 1.2s at
# best and zero during an auto-update.
RMTREE_SETTLE_SECONDS = 2
# Let the copied files settle before the freshly installed presence opens them.
RESTART_DELAY_SECONDS = 5


def verifyPayload(source: Path) -> list[str] | None:
    """Return the missing required files, or None if the folder is unreadable."""
    try:
        return findMissingFiles(os.listdir(source), REQUIRED_DIST_FILES)
    except OSError:
        return None


def main() -> int:
    isUpdate = isUpdateMode(sys.argv)

    with Wizard(
        "hoi4-presence setup",
        "Installs the Discord Rich Presence into your Hearts of Iron IV install.",
        totalSteps=BASE_STEPS + 1 if isUpdate else BASE_STEPS,
        interactive=not isUpdate,
    ) as wizard:
        # Next to setup.exe, not in the working directory: "Run as administrator"
        # launches with cwd set to System32, and the auto-updater launches setup.exe
        # from the folder it unpacked into.
        source = getBaseDir() / SOURCE_SUBPATH

        with wizard.step("Verifying the release files"):
            missing = verifyPayload(source)

        # Outside the step: a `return` is not an exception, so the step would
        # otherwise be marked complete on the way out.
        if missing is None:
            return wizard.fail(f"Could not find the 'dist' directory\n{source}")
        if missing:
            return wizard.fail(f"These files were not found in {source}:\n\n{', '.join(missing)}")

        if isUpdate:
            with wizard.step(f"Stopping any running {PRESENCE_EXE}"):
                # Best effort: taskkill exits 128 when the process is not running,
                # which is the normal case -- the presence exits as soon as the game
                # does. capture_output keeps its stdio off our console.
                subprocess.run(["taskkill", "/f", "/im", PRESENCE_EXE], capture_output=True)

        # 1 - locate the documents folder, recognised by settings.txt
        try:
            with wizard.step("Locating the HOI4 documents folder"):
                documents = findDocumentsDir(defaultDocumentsDir(), wizard.ask, wizard.warn)
        except RuntimeError as error:
            return wizard.fail(f"{error}\n\nRun setup.exe by hand to finish the update.")

        # Copy the payload next to the saves.
        installDir = documents / INSTALL_DIR_NAME
        try:
            with wizard.step(f"Installing the presence into {INSTALL_DIR_NAME}"):
                if installDir.exists():
                    wizard.warn("Old installation found, deleting it first")
                    shutil.rmtree(installDir)
                    time.sleep(RMTREE_SETTLE_SECONDS)
                shutil.copytree(source, installDir)
        except OSError as error:
            return wizard.fail(f"{error}\n\nCan't move the hoi4Presence to the save path")

        # 2 - the presence can only read plaintext saves
        try:
            with wizard.step(f"Writing save_as_binary=no in {SETTINGS_FILE}"):
                settingsPath = documents / SETTINGS_FILE
                settings = settingsPath.read_text(encoding="utf-8")
                settingsPath.write_text(setBinarySaves(settings, enabled=False), encoding="utf-8")
        except (OSError, ValueError) as error:
            return wizard.fail(f"{error}\n\nCan't change the {SETTINGS_FILE}")

        # 3 - locate the game folder, recognised by hoi4.exe
        try:
            with wizard.step("Locating the game folder"):
                gameFolder = findGameDir(defaultGameDir(), wizard.ask, wizard.warn)
        except RuntimeError as error:
            return wizard.fail(f"{error}\n\nRun setup.exe by hand to finish the update.")

        try:
            with wizard.step(f"Installing {SHIM_NAME} into the game folder"):
                shutil.copyfile(source / SHIM_NAME, gameFolder / SHIM_NAME)

                # The shim cannot work the documents folder out for itself, so hand it
                # the one we just resolved. Written unconditionally: doing this only for
                # non-default paths meant a second install from the same extracted
                # folder kept the first install's path.
                (gameFolder / CONFIG_NAME).write_text(str(documents), encoding="utf-8")

                # Upgrades from 1.3.x leave a runRPC.bat here that nothing runs now.
                (gameFolder / LEGACY_BATCH_NAME).unlink(missing_ok=True)
        except OSError as error:
            return wizard.fail(f"{error}\n\nCan't set up the {SHIM_NAME} in the game folder")

        # 4 - point the Paradox launcher at the shim
        try:
            with wizard.step(f"Pointing {LAUNCHER_SETTINGS} at {SHIM_NAME}"):
                launcherPath = gameFolder / LAUNCHER_SETTINGS
                launcher = json.loads(launcherPath.read_text(encoding="utf-8"))
                launcherPath.write_text(
                    json.dumps(setLauncherExe(launcher, install=True), indent=4),
                    encoding="utf-8",
                )
        except (OSError, ValueError) as error:
            return wizard.fail(f"{error}\n\nCan't change the {LAUNCHER_SETTINGS}")

        wizard.flagParade()
        wizard.finish(
            "Success! The hoi4Presence is installed in your game folder.",
            "",
            "Start the game through the Paradox launcher to activate the presence.",
            "Keep uninstall.exe -- it is the only copy, and it is not installed anywhere else.",
            "",
            "See https://github.com/ThiaudioTT/hoi4-presence for updates and more information.",
        )

    if isUpdate:
        time.sleep(RESTART_DELAY_SECONDS)
        # Start the presence itself. Starting the launcher shim would also start
        # hoi4.exe -- on top of the game the user is already playing. Outside the
        # wizard, so the console is ours no longer.
        os.startfile(installDir / PRESENCE_EXE)

    return 0


if __name__ == "__main__":
    sys.exit(main())
