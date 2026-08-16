"""The presence loop.

This is the only module in the package that imports :mod:`pypresence` and
:mod:`psutil`, so everything else stays importable on any platform. The test
suite never imports it.
"""

from __future__ import annotations

import logging
import os
import time

import psutil
from pypresence import Presence

from hoi4presence import saves
from hoi4presence.countries import getCountry
from hoi4presence.paths import GAME_EXE
from hoi4presence.presence import buildIdlePresence, buildPresence
from hoi4presence.saves import SaveHeader, SaveParseError

logger = logging.getLogger(__name__)

CLIENT_ID = "1021549599732809820"

POLL_SECONDS = 30


def isGameRunning(processName: str = GAME_EXE) -> bool:
    """Whether the game is currently running."""
    for process in psutil.process_iter(["name"]):
        try:
            if process.info["name"] == processName:
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return False


def readCurrentSave(savePattern: str, now: float) -> tuple[SaveHeader, str] | None:
    """Return ``(header, path)`` for the newest save if it is fresh, else None."""
    latest = saves.pickLatestSave(saves.findSaves(savePattern))
    if latest is None:
        # Logged at INFO on purpose: this and the staleness message below are the
        # two reasons a presence looks stuck, and the log is what users attach.
        logger.info("No save files matched %s", savePattern)
        return None

    if not saves.isSaveRecent(os.path.getmtime(latest), now):
        logger.info("Newest save %s is older than the freshness window", latest)
        return None

    return saves.parseSaveHeader(saves.readSaveHeader(latest)), latest


def closeQuietly(rpc: Presence) -> None:
    """Drop a Discord connection that may already be dead."""
    try:
        rpc.close()
    except Exception:
        logger.debug("Ignoring an error while closing the Discord connection", exc_info=True)


def run(savePattern: str) -> int:
    """Mirror the game state to Discord until the game exits.

    The connection is (re)established inside the loop rather than once up front:
    Discord is started by the user, not by us, so it may not be up yet when the
    game launches, and it restarts itself often enough that a session-long
    connection cannot be assumed.
    """
    startTime = time.time()
    rpc: Presence | None = None

    logger.info("Watching %s", savePattern)

    while True:
        try:
            current = readCurrentSave(savePattern, time.time())
        except SaveParseError:
            # Most often the user still has save_as_binary=yes, so the save is
            # not readable text. Nothing to do but wait for a usable one.
            logger.warning("Could not read the save header", exc_info=True)
            current = None
        except OSError:
            logger.warning("Could not access the save file", exc_info=True)
            current = None

        try:
            if rpc is None:
                rpc = Presence(CLIENT_ID)
                rpc.connect()
                rpc.update(**buildIdlePresence(startTime))
                logger.info("Connected to Discord.")

            if current is not None:
                header, path = current
                country = getCountry(header.tag)
                rpc.update(**buildPresence(country, header, startTime))
                logger.info("Updated presence from %s: %s in %s", path, country.name, header.year)
        except Exception:
            logger.warning("Could not reach Discord; retrying in %ss. Is it running?", POLL_SECONDS, exc_info=True)
            if rpc is not None:
                closeQuietly(rpc)
                rpc = None

        time.sleep(POLL_SECONDS)

        if not isGameRunning():
            logger.info("%s is no longer running; exiting.", GAME_EXE)
            if rpc is not None:
                closeQuietly(rpc)
            return 0
