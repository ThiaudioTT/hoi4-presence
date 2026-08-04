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
from hoi4presence.presence import buildIdlePresence, buildPresence
from hoi4presence.saves import SaveParseError

logger = logging.getLogger(__name__)

CLIENT_ID = "1021549599732809820"
GAME_PROCESS = "hoi4.exe"

POLL_SECONDS = 30
ERROR_BACKOFF_SECONDS = 5


def isGameRunning(processName: str = GAME_PROCESS) -> bool:
    """Whether the game is currently running."""
    for process in psutil.process_iter(["name"]):
        try:
            if process.name() == processName:
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return False


def readCurrentSave(savePattern: str, now: float) -> tuple[object, str] | None:
    """Return ``(header, path)`` for the newest save if it is fresh, else None."""
    latest = saves.pickLatestSave(saves.findSaves(savePattern))
    if latest is None:
        logger.debug("No save files matched %s", savePattern)
        return None

    if not saves.isSaveRecent(os.path.getmtime(latest), now):
        logger.debug("Newest save %s is older than the freshness window", latest)
        return None

    return saves.parseSaveHeader(saves.readSaveHeader(latest)), latest


def run(savePattern: str) -> int:
    """Connect to Discord and mirror the game state until the game exits."""
    startTime = time.time()

    try:
        rpc = Presence(CLIENT_ID)
        rpc.connect()
        rpc.update(**buildIdlePresence(startTime))
    except Exception:
        logger.exception("Could not connect to Discord. Is it running?")
        time.sleep(ERROR_BACKOFF_SECONDS)
        return 1

    logger.info("Connected to Discord; watching %s", savePattern)

    while True:
        try:
            current = readCurrentSave(savePattern, time.time())
            if current is not None:
                header, path = current
                country = getCountry(header.tag)
                rpc.update(**buildPresence(country, header, startTime))
                logger.info("Updated presence from %s: %s in %s", path, country.name, header.year)
        except SaveParseError:
            # Most often the user still has save_as_binary=yes, so the save is
            # not readable text. Nothing to do but wait for a usable one.
            logger.warning("Could not read the save header", exc_info=True)
            time.sleep(ERROR_BACKOFF_SECONDS)
        except OSError:
            logger.warning("Could not access the save file", exc_info=True)
            time.sleep(ERROR_BACKOFF_SECONDS)
        except Exception:
            logger.exception("Unexpected error while updating the presence")
            time.sleep(ERROR_BACKOFF_SECONDS)

        time.sleep(POLL_SECONDS)

        if not isGameRunning():
            logger.info("%s is no longer running; exiting.", GAME_PROCESS)
            return 0
