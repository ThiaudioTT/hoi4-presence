"""Entry point for setup.exe -- installs the presence into a HOI4 install.

This is a console wizard, so it talks to the user with print() rather than the
logger; the windowed executables are the ones that need a log file.

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

SOURCE_SUBPATH = Path("discordRPC") / "dist"

IS_UPDATE = False


def customInput(prompt: str = "") -> str | None:
    """Wait for the user, unless the auto-updater is driving us headlessly."""
    if not IS_UPDATE:
        return input(prompt)
    return None


def promptForPath(prompt: str) -> str:
    """Ask the user where a folder is. The auto-updater has nobody to ask.

    Raising here rather than blocking matters: an auto-update runs behind the
    game with a console the user is not looking at, and it has already stopped
    the running presence by this point.
    """
    if IS_UPDATE:
        raise RuntimeError("Cannot ask for a folder during an auto-update.")
    return input(prompt)


def fail(message: str, *, delay: int = 10) -> int:
    print(f"\n{message}\n\nExiting...")
    time.sleep(delay)
    return 1


def verifyPayload(source: Path) -> list[str] | None:
    """Return the missing required files, or None if the folder is unreadable."""
    try:
        return findMissingFiles(os.listdir(source), REQUIRED_DIST_FILES)
    except OSError:
        return None


def main() -> int:
    global IS_UPDATE
    IS_UPDATE = isUpdateMode(sys.argv)

    print("This script will install the hoi4-presence in your game/save path\nPress enter to continue...")
    customInput()

    # Next to setup.exe, not in the working directory: "Run as administrator"
    # launches with cwd set to System32, and the auto-updater launches setup.exe
    # from the folder it unpacked into.
    source = getBaseDir() / SOURCE_SUBPATH

    print("Verifying required files...")
    missing = verifyPayload(source)
    if missing is None:
        return fail(f"Error: Could not find the 'dist' directory\n{source}")
    if missing:
        return fail(f"Error: The following files were not found in {source}:\n\n{', '.join(missing)}")
    print("All required files are valid!")

    if IS_UPDATE:
        print("Stopping any running instances of hoi4Presence.exe...")
        # Best effort: taskkill exits 128 when the process is not running, which
        # is the normal case -- the presence exits as soon as the game does.
        subprocess.run(["taskkill", "/f", "/im", PRESENCE_EXE], capture_output=True)

    # 1 - locate the documents folder, recognised by settings.txt
    try:
        documents = findDocumentsDir(defaultDocumentsDir(), promptForPath, print)
    except RuntimeError as error:
        return fail(f"{error}\nRun setup.exe by hand to finish the update.", delay=3)
    print("Documents directory found")

    # Copy the payload next to the saves.
    installDir = documents / INSTALL_DIR_NAME
    try:
        if installDir.exists():
            print("Old installation found, deleting...")
            shutil.rmtree(installDir)
            time.sleep(2)
        print(f"\nMoving...\n{documents}\n{installDir}")
        shutil.copytree(source, installDir)
    except OSError as error:
        return fail(f"{error}\nCan't move the hoi4Presence to the save Path", delay=3)

    # 2 - the presence can only read plaintext saves
    try:
        settingsPath = documents / SETTINGS_FILE
        print(f"Writing save_as_binary=no in {SETTINGS_FILE}...")
        settings = settingsPath.read_text(encoding="utf-8")
        settingsPath.write_text(setBinarySaves(settings, enabled=False), encoding="utf-8")
    except (OSError, ValueError) as error:
        return fail(f"{error}\nCan't change the {SETTINGS_FILE}", delay=3)

    # 3 - locate the game folder, recognised by hoi4.exe
    try:
        gameFolder = findGameDir(defaultGameDir(), promptForPath, print)
    except RuntimeError as error:
        return fail(f"{error}\nRun setup.exe by hand to finish the update.", delay=3)
    print("Game directory found")

    try:
        print(f"Moving {SHIM_NAME} to the game folder...\n{gameFolder}")
        shutil.copyfile(source / SHIM_NAME, gameFolder / SHIM_NAME)

        # The shim cannot work the documents folder out for itself, so hand it
        # the one we just resolved. Written unconditionally: doing this only for
        # non-default paths meant a second install from the same extracted
        # folder kept the first install's path.
        print(f"Writing {CONFIG_NAME}...")
        (gameFolder / CONFIG_NAME).write_text(str(documents), encoding="utf-8")

        # Upgrades from 1.3.x leave a runRPC.bat here that nothing runs now.
        (gameFolder / LEGACY_BATCH_NAME).unlink(missing_ok=True)
    except OSError as error:
        return fail(f"{error}\nCan't set up the {SHIM_NAME} in the game folder", delay=3)

    # 4 - point the Paradox launcher at the shim
    try:
        print(f"Changing {LAUNCHER_SETTINGS}...")
        launcherPath = gameFolder / LAUNCHER_SETTINGS
        launcher = json.loads(launcherPath.read_text(encoding="utf-8"))
        launcherPath.write_text(
            json.dumps(setLauncherExe(launcher, install=True), indent=4),
            encoding="utf-8",
        )
    except (OSError, ValueError) as error:
        return fail(f"{error}\nCan't change the {LAUNCHER_SETTINGS}", delay=3)

    print("\n\nSuccess! The hoi4Presence is installed in your game folder.\n\n")
    print("Execute the game via launcher to auto activate the presence.\n\n")
    print("Keep uninstall.exe -- it is the only copy, and it is not installed anywhere else.\n\n")
    print("See https://github.com/ThiaudioTT/hoi4-presence for updates and more information.\n\n")

    customInput()
    time.sleep(5)

    if IS_UPDATE:
        # Start the presence itself. Starting the launcher shim would also start
        # hoi4.exe -- on top of the game the user is already playing.
        os.startfile(installDir / PRESENCE_EXE)

    return 0


if __name__ == "__main__":
    sys.exit(main())
