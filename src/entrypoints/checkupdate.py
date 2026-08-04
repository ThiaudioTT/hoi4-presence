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
    setupLogging(getBaseDir(__file__))
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

    downloadPath = downloadUpdate()
    if downloadPath is None:
        return 0

    installer = Path(downloadPath) / INSTALLER_NAME
    logger.info("Updating...")

    # Hand over to setup.exe, which reinstalls and restarts the presence. Passing
    # cwd so the installer knows where the freshly unpacked files are.
    subprocess.Popen([str(installer), "-update"], start_new_session=True, cwd=downloadPath)

    logger.info("Closing checkupdate...")
    return 0


if __name__ == "__main__":
    sys.exit(main())
