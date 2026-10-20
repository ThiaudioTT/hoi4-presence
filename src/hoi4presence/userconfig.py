from __future__ import annotations

import json
import logging
import os
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)

CONFIG_FILE = "hoi4Presence-settings.json"

STATUS_TEXT_CHOICES = ("game", "country")
DEFAULT_STATUS_TEXT = "game"

MOD_LINE_CHOICES = ("auto", "all")
DEFAULT_MOD_LINE = "auto"

TEMPLATE = {
    "_help": "Discord presence settings. Save the file and Discord updates within a minute.",
    "show_mods": True,
    "_help_mod_line": (
        '"auto": the overhaul (The Fire Rises, The Road to 56...) and its submods by name, then a count '
        'of the others ("The Road to 56 + Road to 56 : Expanded + 8 mods"). "all": every mod by name.'
    ),
    "mod_line": DEFAULT_MOD_LINE,
    "_help_pinned_mods": 'In "auto" mode, mods to name anyway instead of counting them.',
    "pinned_mods": [],
    "_help_hidden_mods": "Mods never shown nor counted, by their exact launcher name.",
    "hidden_mods": [],
    "_help_mod_names": 'Shorter names for mods: "Full launcher name": "Short name".',
    "mod_names": {},
    "_help_status_text": (
        'What Discord shows after "Playing" next to your name in the member list: '
        '"game" (Hearts of Iron IV) or "country".'
    ),
    "status_text": DEFAULT_STATUS_TEXT,
    "_help_countries": (
        'Override a country by its three-letter tag: "TAG": {"name": "...", "flag": "https://....png"}. '
        "Both fields are optional."
    ),
    "countries": {},
}


@dataclass(frozen=True)
class CountryOverride:
    name: str | None = None
    flag: str | None = None


@dataclass(frozen=True)
class UserConfig:
    showMods: bool = True
    statusText: str = DEFAULT_STATUS_TEXT
    modLine: str = DEFAULT_MOD_LINE
    pinnedMods: tuple[str, ...] = ()
    hiddenMods: tuple[str, ...] = ()
    modNames: Mapping[str, str] = field(default_factory=dict)
    countries: Mapping[str, CountryOverride] = field(default_factory=dict)


def _text(value: object) -> str | None:
    return value.strip() if isinstance(value, str) and value.strip() else None


def _choice(data: dict, key: str, choices: tuple[str, ...], default: str) -> str:
    value = data.get(key, default)
    if value not in choices:
        logger.warning("Unknown %s %r; expected one of %s", key, value, choices)
        return default
    return value


def _names(value: object) -> tuple[str, ...]:
    return tuple(name for name in value if _text(name)) if isinstance(value, list) else ()


def parseUserConfig(data: object) -> UserConfig:
    if not isinstance(data, dict):
        return UserConfig()

    showMods = data.get("show_mods", True)
    names = data.get("mod_names", {})
    countries = data.get("countries", {})

    overrides: dict[str, CountryOverride] = {}
    if isinstance(countries, dict):
        for tag, entry in countries.items():
            if not isinstance(entry, dict) or not _text(tag):
                continue
            flag = _text(entry.get("flag"))
            if flag and not flag.startswith("https://"):
                logger.warning("Ignoring the flag for %s: it must be an https:// link", tag)
                flag = None
            overrides[tag.strip().upper()] = CountryOverride(name=_text(entry.get("name")), flag=flag)

    return UserConfig(
        showMods=showMods if isinstance(showMods, bool) else True,
        statusText=_choice(data, "status_text", STATUS_TEXT_CHOICES, DEFAULT_STATUS_TEXT),
        modLine=_choice(data, "mod_line", MOD_LINE_CHOICES, DEFAULT_MOD_LINE),
        pinnedMods=_names(data.get("pinned_mods", [])),
        hiddenMods=_names(data.get("hidden_mods", [])),
        modNames={k: v for k, v in names.items() if _text(k) and _text(v)} if isinstance(names, dict) else {},
        countries=overrides,
    )


def configPath(documentsDir: str | os.PathLike[str]) -> Path:
    return Path(documentsDir) / CONFIG_FILE


def loadUserConfig(documentsDir: str | os.PathLike[str]) -> UserConfig:
    try:
        text = configPath(documentsDir).read_text(encoding="utf-8-sig")
    except FileNotFoundError:
        return UserConfig()
    except OSError:
        logger.warning("Could not read %s", CONFIG_FILE, exc_info=True)
        return UserConfig()

    try:
        return parseUserConfig(json.loads(text))
    except ValueError as error:
        logger.warning("%s is not valid JSON (%s); using the default settings", CONFIG_FILE, error)
        return UserConfig()


def ensureConfigFile(documentsDir: str | os.PathLike[str]) -> None:
    path = configPath(documentsDir)
    if path.exists() or not Path(documentsDir).is_dir():
        return
    try:
        path.write_text(json.dumps(TEMPLATE, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        logger.info("Wrote a settings template to %s", path)
    except OSError:
        logger.warning("Could not write %s", path, exc_info=True)
