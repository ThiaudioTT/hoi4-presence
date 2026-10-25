from __future__ import annotations

import logging
import re
from collections.abc import Iterable, Sequence
from pathlib import Path

logger = logging.getLogger(__name__)

LOCALISATION_DIR = "localisation"
ENGLISH = "l_english"

LOC_LINE = re.compile(r'^\s*([A-Za-z0-9_.\-]+):\d*\s*"(.*)"')
LANGUAGE_HEADER = re.compile(r"^\s*(l_[a-z_]+)\s*:\s*$")
SETTINGS_LANGUAGE = re.compile(r'^\s*language\s*=\s*"?(l_[a-z_]+)"?', re.MULTILINE)
COLOUR_CODE = re.compile(r"§.")

Entries = dict[tuple[str, str], str]


def readGameLanguage(settingsText: str) -> str | None:
    match = SETTINGS_LANGUAGE.search(settingsText)
    return match[1] if match else None


def cleanName(raw: str) -> str | None:
    text = COLOUR_CODE.sub("", raw).replace('\\"', '"').strip()
    if not text or "[" in text or "$" in text:
        return None
    return text


def scanText(text: str, tag: str, entries: Entries) -> None:
    language = None
    prefix = tag.upper()
    for line in text.splitlines():
        if language is None:
            header = LANGUAGE_HEADER.match(line)
            if header:
                language = header[1]
            continue
        if not line.lstrip().startswith(prefix):
            continue
        match = LOC_LINE.match(line)
        if not match:
            continue
        key = match[1]
        if key == prefix or (key.startswith(prefix + "_") and key[len(prefix) + 1 :].islower()):
            entries[(language, key)] = match[2]


def localisationFiles(contentDir: Path) -> tuple[list[Path], list[Path]]:
    root = contentDir / LOCALISATION_DIR
    if not root.is_dir():
        return [], []
    files = sorted(root.rglob("*.yml"))

    def isReplace(path: Path) -> bool:
        return "replace" in path.relative_to(root).parts

    return [path for path in files if not isReplace(path)], [path for path in files if isReplace(path)]


def collectEntries(tag: str, contentDirs: Iterable[Path]) -> Entries:
    ordinary: list[Path] = []
    replacing: list[Path] = []
    for contentDir in contentDirs:
        files, replaceFiles = localisationFiles(contentDir)
        ordinary.extend(files)
        replacing.extend(replaceFiles)

    entries: Entries = {}
    for path in ordinary + replacing:
        try:
            text = path.read_text(encoding="utf-8-sig", errors="ignore")
        except OSError:
            continue
        scanText(text, tag, entries)
    return entries


def pickName(entries: Entries, tag: str, ideology: str, languages: Sequence[str]) -> str | None:
    for language in languages:
        for key in (f"{tag}_{ideology}", tag):
            name = cleanName(entries.get((language, key), ""))
            if name:
                return name
    return None


class CountryNames:
    def __init__(self) -> None:
        self._cache: dict[tuple[str, tuple[Path, ...]], Entries] = {}

    def lookup(self, tag: str, ideology: str, contentDirs: Sequence[Path], gameLanguage: str | None) -> str | None:
        if not contentDirs:
            return None
        key = (tag.upper(), tuple(contentDirs))
        if key not in self._cache:
            self._cache[key] = collectEntries(tag, contentDirs)
            logger.info("Found %d localisation entries for %s in the enabled mods", len(self._cache[key]), tag)

        languages = [lang for lang in (gameLanguage, ENGLISH) if lang]
        return pickName(self._cache[key], tag.upper(), ideology, list(dict.fromkeys(languages)))
