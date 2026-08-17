"""Reading and parsing HOI4 save headers.

A plaintext save starts with a fixed block of ``key=value`` lines::

    HOI4txt
    player="GER"
    ideology=fascism
    date="1936.1.1.12"
    difficulty="normal"
    version="Operation Postern v1.19.2.0.a729 (d245)"
    ironman="Ironman Finland 1.hoi4"

Only those first few lines are ever read, and the handle is closed immediately:
HOI4 needs write access to the file it is autosaving into.
"""

from __future__ import annotations

import glob
import os
import re
from collections.abc import Callable, Iterable
from dataclasses import dataclass

# How many lines of the save to read. Only five are needed today, but the parse is
# key-driven, so reading a wider window costs nothing and keeps a HOI4 patch that
# inserts one header field from pushing `difficulty` out of range.
HEADER_LINES = 20

# A save older than this is left over from a previous session, so the presence
# ignores it rather than reporting a stale country.
FRESHNESS_WINDOW_SECONDS = 120

REQUIRED_FIELDS = ("player", "ideology", "date", "difficulty")

MONTHS = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")

# "Operation Postern v1.19.2.0.a729 (d245)" -> the patch name and its first three
# components. The build hash and the fourth number are noise on a presence.
VERSION_PATTERN = re.compile(r"(.+?) v(\d+\.\d+\.\d+)")


class SaveParseError(ValueError):
    """Raised when a save header is truncated or missing fields we need."""


@dataclass(frozen=True)
class SaveHeader:
    """The save fields the presence displays.

    ``version`` and ``ironman`` are optional rather than required: only ironman
    saves carry an ``ironman`` key at all, and a save from an old enough patch
    may predate ``version``. Neither is worth failing a parse over.
    """

    tag: str
    ideology: str
    date: str
    difficulty: str
    version: str = ""
    ironman: bool = False

    @property
    def year(self) -> str:
        """The in-game year, e.g. ``"1936"`` from ``"1936.1.1.12"``."""
        return self.date[:4]

    @property
    def dateLabel(self) -> str:
        """The in-game date, e.g. ``"1 Mar 1936"`` from ``"1936.3.1.2"``."""
        parts = self.date.split(".")
        if len(parts) < 3 or not all(part.isdigit() for part in parts[:3]):
            return self.date

        year, month, day = parts[:3]
        if not 1 <= int(month) <= 12:
            return self.date
        return f"{int(day)} {MONTHS[int(month) - 1]} {year}"

    @property
    def versionLabel(self) -> str:
        """The patch, e.g. ``"Operation Postern 1.19.2"``, or the raw string."""
        match = VERSION_PATTERN.match(self.version)
        return f"{match[1]} {match[2]}" if match else self.version


def findSaves(pattern: str) -> list[str]:
    """Return every save matching ``pattern``."""
    return glob.glob(pattern)


def pickLatestSave(
    paths: Iterable[str],
    mtime: Callable[[str], float] = os.path.getmtime,
) -> str | None:
    """Return the most recently modified save, or None when there are none.

    The caller used to run ``max()`` straight on the glob, which raises on an
    empty directory and was swallowed by a broad except, leaving no diagnostic.
    """
    candidates = list(paths)
    if not candidates:
        return None
    return max(candidates, key=mtime)


def isSaveRecent(mtime: float, now: float, window: float = FRESHNESS_WINDOW_SECONDS) -> bool:
    """Whether a save modified at ``mtime`` is fresh enough to report."""
    return (now - mtime) <= window


def readSaveHeader(path: str | os.PathLike[str]) -> str:
    """Read the header block of a save and close the file straight away."""
    lines: list[str] = []
    with open(path, encoding="utf-8", errors="ignore") as handle:
        for _ in range(HEADER_LINES):
            line = handle.readline()
            if not line:
                break
            lines.append(line)
    return "".join(lines)


def parseSaveHeader(text: str) -> SaveHeader:
    """Parse a save header block into a :class:`SaveHeader`.

    Parsing is key-driven rather than positional, so a reordered or extra line
    does not silently shift every field by one.
    """
    fields: dict[str, str] = {}
    for line in text.splitlines()[:HEADER_LINES]:
        key, separator, value = line.partition("=")
        if not separator:
            continue
        fields[key.strip()] = value.strip().strip('"')

    missing = [name for name in REQUIRED_FIELDS if not fields.get(name)]
    if missing:
        raise SaveParseError(f"save header is missing {', '.join(missing)}")

    return SaveHeader(
        tag=fields["player"],
        ideology=fields["ideology"],
        date=fields["date"],
        difficulty=fields["difficulty"],
        version=fields.get("version", ""),
        # The key exists only in ironman saves; its value is the save's own name.
        ironman="ironman" in fields,
    )
