from __future__ import annotations

import json
import logging
import os
import re
from dataclasses import dataclass, field
from pathlib import Path

from hoi4presence.countries import Country, getCountry, withOverrides
from hoi4presence.localisation import CountryNames, cleanName, readGameLanguage
from hoi4presence.mods import Mod, modLabel, readEnabledMods
from hoi4presence.paths import SETTINGS_FILE
from hoi4presence.saves import SaveHeader
from hoi4presence.userconfig import UserConfig, loadUserConfig

logger = logging.getLogger(__name__)

CONTINUE_GAME_FILE = "continue_game.json"
TRAILING_DATE = re.compile(r"\s+\d{1,4}\.\d{1,2}\.\d{1,2}(\.\d{1,2})?\s*$")


@dataclass(frozen=True)
class Session:
    mods: tuple[Mod, ...] = ()
    gameLanguage: str | None = None
    config: UserConfig = field(default_factory=UserConfig)
    continueGame: dict | None = None

    @property
    def modLine(self) -> str:
        if not self.config.showMods:
            return ""
        return modLabel(
            self.mods,
            hidden=self.config.hiddenMods,
            renames=self.config.modNames,
            showAll=self.config.modLine == "all",
            pinned=self.config.pinnedMods,
        )

    @property
    def contentDirs(self) -> list[Path]:
        return [mod.contentDir for mod in self.mods if mod.contentDir is not None]


def _readJson(path: Path) -> dict | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
    except FileNotFoundError:
        return None
    except (OSError, ValueError):
        logger.info("Could not read %s", path.name, exc_info=True)
        return None
    return data if isinstance(data, dict) else None


def readSession(documentsDir: str | os.PathLike[str] | None) -> Session:
    if documentsDir is None:
        return Session()
    documentsDir = Path(documentsDir)

    try:
        language = readGameLanguage((documentsDir / SETTINGS_FILE).read_text(encoding="utf-8-sig", errors="ignore"))
    except OSError:
        language = None

    return Session(
        mods=tuple(readEnabledMods(documentsDir)),
        gameLanguage=language,
        config=loadUserConfig(documentsDir),
        continueGame=_readJson(documentsDir / CONTINUE_GAME_FILE),
    )


def readContinueGameName(continueGame: dict | None, savePath: str | os.PathLike[str] | None) -> str | None:
    if not continueGame or savePath is None:
        return None
    filename = continueGame.get("filename")
    title = continueGame.get("title")
    if not isinstance(filename, str) or not isinstance(title, str):
        return None
    if filename.casefold() != re.split(r"[\\/]", str(savePath))[-1].casefold():
        return None
    return cleanName(TRAILING_DATE.sub("", title))


def resolveCountry(
    header: SaveHeader,
    session: Session,
    names: CountryNames,
    savePath: str | os.PathLike[str] | None = None,
) -> Country:
    country = getCountry(header.tag)
    override = session.config.countries.get(header.tag.upper())

    name = (override.name if override else None) or readContinueGameName(session.continueGame, savePath)
    if not name:
        try:
            name = names.lookup(header.tag, header.ideology, session.contentDirs, session.gameLanguage)
        except OSError:
            logger.warning("Could not read the mods' localisation", exc_info=True)

    return withOverrides(country, name=name, flag=override.flag if override else None)
