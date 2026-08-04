"""Reading and parsing HOI4 save headers.

A plaintext save starts with a fixed block of ``key=value`` lines::

    HOI4txt
    player="GER"
    ideology=fascism
    date="1936.1.1.12"
    difficulty="normal"

Only those first few lines are ever read, and the handle is closed immediately:
HOI4 needs write access to the file it is autosaving into.
"""

from __future__ import annotations

import glob
import os
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


class SaveParseError(ValueError):
    """Raised when a save header is truncated or missing fields we need."""


@dataclass(frozen=True)
class SaveHeader:
    """The four fields the presence displays."""

    tag: str
    ideology: str
    date: str
    difficulty: str

    @property
    def year(self) -> str:
        """The in-game year, e.g. ``"1936"`` from ``"1936.1.1.12"``."""
        return self.date[:4]


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
    )
