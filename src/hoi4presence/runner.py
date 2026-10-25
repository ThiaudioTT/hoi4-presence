"""The presence loop.

This is the only module in the package that imports :mod:`pypresence` and
:mod:`psutil`, so everything else stays importable on any platform. The test
suite never imports it.
"""

from __future__ import annotations

import logging
import os
import time
from pathlib import Path

import psutil
from pypresence import Presence
from pypresence.types import StatusDisplayType

from hoi4presence import saves
from hoi4presence.localisation import CountryNames
from hoi4presence.paths import GAME_EXE
from hoi4presence.presence import buildIdlePresence, buildPresence
from hoi4presence.saves import SaveHeader, SaveParseError
from hoi4presence.session import readSession, resolveCountry
from hoi4presence.userconfig import ensureConfigFile

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


def toPypresence(payload: dict[str, object]) -> dict[str, object]:
    if "status_display_type" not in payload:
        return payload
    return {**payload, "status_display_type": StatusDisplayType(payload["status_display_type"])}


def closeQuietly(rpc: Presence) -> None:
    """Drop a Discord connection that may already be dead."""
    try:
        rpc.close()
    except Exception:
        logger.debug("Ignoring an error while closing the Discord connection", exc_info=True)


def run(savePattern: str, documentsDir: Path | None = None) -> int:
    """Mirror the game state to Discord until the game exits.

    The connection is (re)established inside the loop rather than once up front:
    Discord is started by the user, not by us, so it may not be up yet when the
    game launches, and it restarts itself often enough that a session-long
    connection cannot be assumed.
    """
    startTime = time.time()
    rpc: Presence | None = None
    names = CountryNames()
    lastPayload: dict[str, object] | None = None
    showingIdle = True
    lastModLine: str | None = None

    logger.info("Watching %s", savePattern)
    if documentsDir is not None:
        ensureConfigFile(documentsDir)

    while True:
        session = readSession(documentsDir)
        if session.modLine != lastModLine:
            logger.info("Mods (%d enabled): %s", len(session.mods), session.modLine or "none shown")
            lastModLine = session.modLine
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
                lastPayload = None
                logger.info("Connected to Discord.")

            if current is not None:
                header, path = current
                country = resolveCountry(header, session, names, path)
                payload = buildPresence(country, header, startTime, session.modLine, session.config.statusText)
                source = path
                showingIdle = False
            elif showingIdle:
                payload = buildIdlePresence(startTime)
                source = "launcher"
            else:
                payload, source = lastPayload, ""

            if payload != lastPayload:
                rpc.update(**toPypresence(payload))
                lastPayload = payload
                logger.info(
                    "Updated presence from %s: %s | %s", source, payload.get("details"), payload.get("state", "")
                )
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
