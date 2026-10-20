from __future__ import annotations

import json
import logging
import os
import re
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)

DLC_LOAD_FILE = "dlc_load.json"
MOD_SEPARATOR = " + "
VANILLA_LABEL = "Vanilla"

DESCRIPTOR_LINE = re.compile(r'^\s*([A-Za-z_]+)\s*=\s*"([^"]*)"')
BLOCK_OPEN = re.compile(r"^\s*([A-Za-z_]+)\s*=\s*\{")
QUOTED = re.compile(r'"([^"]*)"')

WORLD_PATHS = (
    "history/countries",
    "history/states",
    "common/national_focus",
    "common/countries",
    "events",
)


@dataclass(frozen=True)
class Mod:
    name: str
    contentDir: Path | None = None
    replacePaths: tuple[str, ...] = ()
    dependencies: tuple[str, ...] = ()

    @property
    def isOverhaul(self) -> bool:
        return any(path.strip("/").startswith(WORLD_PATHS) for path in self.replacePaths)


@dataclass(frozen=True)
class Descriptor:
    fields: dict[str, str]
    replacePaths: tuple[str, ...]
    blocks: dict[str, tuple[str, ...]]


def parseDescriptor(text: str) -> Descriptor:
    fields: dict[str, str] = {}
    replacePaths: list[str] = []
    blocks: dict[str, list[str]] = {}
    depth = 0
    current: str | None = None

    for line in text.splitlines():
        if depth == 0:
            opened = BLOCK_OPEN.match(line)
            if opened:
                current = opened[1]
                blocks.setdefault(current, [])
                blocks[current].extend(QUOTED.findall(line[opened.end() :].split("}")[0]))
            else:
                match = DESCRIPTOR_LINE.match(line)
                if match and match[1] == "replace_path":
                    replacePaths.append(match[2].strip())
                elif match and match[1] not in fields:
                    fields[match[1]] = match[2].strip()
        elif depth == 1 and current is not None:
            blocks[current].extend(QUOTED.findall(line.split("}")[0]))

        depth += line.count("{") - line.count("}")
        depth = max(depth, 0)
        if depth == 0:
            current = None

    return Descriptor(
        fields=fields,
        replacePaths=tuple(replacePaths),
        blocks={key: tuple(value.strip() for value in values if value.strip()) for key, values in blocks.items()},
    )


def resolvePath(raw: str, documentsDir: Path) -> Path:
    normalised = raw.replace("\\", "/")
    path = Path(normalised)
    return path if path.is_absolute() or re.match(r"^[A-Za-z]:/", normalised) else documentsDir / path


def readDescriptor(descriptorPath: Path, documentsDir: Path) -> Mod | None:
    try:
        text = descriptorPath.read_text(encoding="utf-8-sig", errors="ignore")
    except OSError:
        logger.info("Enabled mod descriptor %s could not be read", descriptorPath)
        return None

    descriptor = parseDescriptor(text)
    fields = descriptor.fields
    name = fields.get("name") or descriptorPath.stem
    rawPath = fields.get("path") or fields.get("archive")
    return Mod(
        name=name,
        contentDir=resolvePath(rawPath, documentsDir) if rawPath else None,
        replacePaths=descriptor.replacePaths,
        dependencies=descriptor.blocks.get("dependencies", ()),
    )


def readEnabledMods(documentsDir: str | os.PathLike[str]) -> list[Mod]:
    documentsDir = Path(documentsDir)
    try:
        data = json.loads((documentsDir / DLC_LOAD_FILE).read_text(encoding="utf-8-sig"))
    except FileNotFoundError:
        return []
    except (OSError, ValueError):
        logger.warning("Could not read %s", DLC_LOAD_FILE, exc_info=True)
        return []

    entries = data.get("enabled_mods", []) if isinstance(data, dict) else []
    mods: list[Mod] = []
    for entry in entries:
        if not isinstance(entry, str) or not entry.strip():
            continue
        mod = readDescriptor(resolvePath(entry.strip(), documentsDir), documentsDir)
        if mod is not None:
            mods.append(mod)
    return mods


def _key(name: str) -> str:
    return name.strip().casefold()


def featuredMods(mods: Sequence[Mod], pinned: Iterable[str] = ()) -> list[Mod]:
    overhauls = [mod for mod in mods if mod.isOverhaul]
    overhaulKeys = {_key(mod.name) for mod in overhauls}
    submods = [
        mod
        for mod in mods
        if not mod.isOverhaul and any(_key(dependency) in overhaulKeys for dependency in mod.dependencies)
    ]
    pinnedKeys = {_key(name) for name in pinned}
    chosen = overhauls + submods
    return chosen + [mod for mod in mods if _key(mod.name) in pinnedKeys and mod not in chosen]


def modLabel(
    mods: Sequence[Mod],
    hidden: Iterable[str] = (),
    renames: Mapping[str, str] | None = None,
    showAll: bool = False,
    pinned: Iterable[str] = (),
) -> str:
    hiddenKeys = {_key(name) for name in hidden}
    renameKeys = {_key(key): value.strip() for key, value in (renames or {}).items()}

    def label(mod: Mod) -> str:
        return renameKeys.get(_key(mod.name)) or mod.name.strip()

    visible = [mod for mod in mods if _key(mod.name) not in hiddenKeys and _key(label(mod)) not in hiddenKeys]
    if not visible:
        return ""

    named = visible if showAll else featuredMods(visible, pinned)
    shown: list[str] = []
    for mod in named:
        if label(mod) not in shown:
            shown.append(label(mod))

    others = len(visible) - len(named)
    if not shown:
        shown.append(VANILLA_LABEL)
    if others:
        shown.append(f"{others} mod" + ("s" if others > 1 else ""))
    return MOD_SEPARATOR.join(shown)
