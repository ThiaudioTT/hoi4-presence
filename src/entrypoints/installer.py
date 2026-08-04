"""Entry point for setup.exe -- installs the presence into a HOI4 install.

This is a console wizard, so it talks to the user with print() rather than the
logger; the windowed executables are the ones that need a log file.

What it does, in order:

1. verify the unpacked release contains everything it needs;
2. stop a running presence (auto-update only);
3. locate the HOI4 documents folder and copy the payload into it;
4. turn off binary saves, so the presence can read them;
5. locate the game folder and drop the launcher shim in;
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
import time

from hoi4presence.install.steps import (
    REQUIRED_DIST_FILES,
    findMissingFiles,
    isUpdateMode,
    rewriteBatchDocumentsPath,
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

SOURCE_SUBPATH = Path("discordRPC") / "dist"
LAUNCHER_SETTINGS = "launcher-settings.json"
BATCH_NAME = "runRPC.bat"
SHIM_NAME = "runRPC.exe"
PRESENCE_EXE = "hoi4Presence.exe"

# cmd.exe reads a .bat in the console codepage, not UTF-8. Writing the documents
# path as UTF-8 would corrupt any non-ASCII character in it -- and this rewrite
# only happens for non-default paths, i.e. exactly the ones likely to have them.
BATCH_ENCODING = "oem" if os.name == "nt" else "utf-8"

IS_UPDATE = False


def customInput(prompt: str = "") -> str | None:
    """Wait for the user, unless the auto-updater is driving us headlessly."""
    if not IS_UPDATE:
        return input(prompt)
    return None


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

    source = Path(os.path.abspath(os.curdir)) / SOURCE_SUBPATH

    print("Verifying required files...")
    missing = verifyPayload(source)
    if missing is None:
        return fail(f"Error: Could not find the 'dist' directory\n{source}")
    if missing:
        return fail(f"Error: The following files were not found in {source}:\n\n{', '.join(missing)}")
    print("All required files are valid!")

    if IS_UPDATE:
        print("Stopping any running instances of hoi4Presence.exe...")
        if os.system(f"taskkill /f /im {PRESENCE_EXE}") != 0:
            return fail("Error occurred while terminating the process.", delay=3)
        print("Process terminated successfully.")

    # 1 - locate the documents folder, recognised by settings.txt
    defaultDocuments = defaultDocumentsDir()
    documents = findDocumentsDir(defaultDocuments, input, print)
    print("Documents directory found")

    # The batch file hardcodes the documents path, so rewrite it when the user
    # keeps their saves somewhere other than the default.
    batchPath = source / BATCH_NAME
    if documents != defaultDocuments:
        print("Updating the runRPC.bat...\n")
        try:
            lines = batchPath.read_text(encoding=BATCH_ENCODING).splitlines(keepends=True)
            batchPath.write_text(
                "".join(rewriteBatchDocumentsPath(lines, str(documents))),
                encoding=BATCH_ENCODING,
            )
        # ValueError covers both an empty runRPC.bat and an undecodable one.
        except (OSError, ValueError) as error:
            return fail(f"{error}\nCan't change the runRPC.bat")

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
    gameFolder = findGameDir(defaultGameDir(), input, print)
    print("Game directory found")

    try:
        print(f"Moving {BATCH_NAME} and {SHIM_NAME} to the game folder...\n{gameFolder}")
        shutil.copyfile(batchPath, gameFolder / BATCH_NAME)
        shutil.copyfile(source / SHIM_NAME, gameFolder / SHIM_NAME)
    except OSError as error:
        return fail(f"{error}\nCan't move the {BATCH_NAME} to the game folder", delay=3)

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
    print("Execute the game via launcher to auto activate the presence.\n\nYou can delete this folder now.\n\n")
    print("See https://github.com/ThiaudioTT/hoi4-presence for updates and more information.\n\n")

    customInput()
    time.sleep(5)

    if IS_UPDATE:
        # The launcher target is the shim, not the batch file it runs.
        os.startfile(gameFolder / SHIM_NAME)

    return 0


if __name__ == "__main__":
    sys.exit(main())
