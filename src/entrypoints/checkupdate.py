"""Entry point for checkupdate.exe -- installs a newer release if one exists."""

from __future__ import annotations

import sys
from pathlib import Path

if not getattr(sys, "frozen", False):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import logging
import subprocess
import time
import urllib.request

from hoi4presence.logging_setup import setupLogging
from hoi4presence.paths import getBaseDir
from hoi4presence.ui import Wizard
from hoi4presence.updater.download import downloadUpdate
from hoi4presence.updater.version_check import (
    REMOTE_VERSION_URL,
    ManifestError,
    loadLocalVersion,
    parseManifest,
    shouldAutoUpdate,
)

logger = logging.getLogger("checkupdate")

INSTALLER_NAME = "setup.exe"
ERROR_BACKOFF_SECONDS = 5


def versionDir() -> Path:
    """Where to look for version.json.

    Installed, it sits next to the executable. From a source checkout the only
    copy is the one at the repository root, which is also what the build ships.
    """
    if getattr(sys, "frozen", False):
        return getBaseDir()
    return Path(__file__).resolve().parents[2]


def main() -> int:
    # Its own file: the launcher shim starts this and hoi4Presence.exe together,
    # and a RotatingFileHandler shared between two processes breaks on rollover.
    #
    # stream=False because the console below belongs to the Wizard. A
    # StreamHandler made here binds sys.stderr for good, so its records would
    # print straight over the progress bar rather than through it.
    setupLogging(getBaseDir(__file__), fileName="checkupdate.log", stream=False)
    logger.info("Checking for updates in hoi4 presence...")

    try:
        local = loadLocalVersion(versionDir())
    except ManifestError:
        logger.exception("Could not read version.json")
        time.sleep(ERROR_BACKOFF_SECONDS)
        return 1

    logger.info("Local version: %s", local["version"])

    try:
        with urllib.request.urlopen(REMOTE_VERSION_URL, timeout=30) as response:
            remote = parseManifest(response.read().decode("utf-8"))
    except Exception:
        logger.exception("Could not check for updates; starting the current version.")
        return 0

    if not shouldAutoUpdate(local, remote):
        logger.info("Version %s is up to date.", local["version"])
        return 0

    logger.info("Update found: %s", remote["version"])

    # Only now is there anything worth showing. Up to here this runs on every
    # single launch and must stay quiet and fast, because the game is starting
    # behind it.
    #
    # interactive=False: there is a console, but the shim started it alongside
    # the game and nobody is sitting at it.
    with Wizard(
        "hoi4-presence update",
        f"Updating {local['version']} to {remote['version']}.",
        totalSteps=1,
        interactive=False,
    ) as wizard:
        # The tag has to be exactly "v<version>" for the asset name to match what
        # build.spec produces. See AGENTS.md.
        try:
            with wizard.step(f"Downloading hoi4-presence v{remote['version']}") as onProgress:
                downloadPath = downloadUpdate(f"v{remote['version']}", onProgress=onProgress)
                # Raised rather than checked after the step, so the step is marked
                # failed instead of reporting a tick above a failure panel.
                # downloadUpdate has already logged why.
                if downloadPath is None:
                    raise RuntimeError("Could not download the update.")
        except RuntimeError as error:
            wizard.fail(f"{error}\n\nStarting the current version instead.")
            return 0

        wizard.finish(f"Downloaded. Handing over to {INSTALLER_NAME}.")

    installer = Path(downloadPath) / INSTALLER_NAME
    logger.info("Updating...")

    # Hand over to setup.exe, which reinstalls and restarts the presence. Passing
    # cwd so the installer knows where the freshly unpacked files are.
    #
    # Outside the wizard on purpose: start_new_session does not give the child a
    # new console on Windows, so setup.exe draws on this one. Ours has to be
    # finished with it -- live region erased, cursor restored -- before it starts.
    subprocess.Popen([str(installer), "-update"], start_new_session=True, cwd=downloadPath)

    logger.info("Closing checkupdate...")
    return 0


if __name__ == "__main__":
    sys.exit(main())
