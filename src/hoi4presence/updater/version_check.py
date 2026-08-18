"""Comparing the installed version against the one published on GitHub.

Deliberately free of :mod:`requests` so the test suite need not install it.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from semantic_version import Version

VERSION_FILE = "version.json"

# Where the published manifest lives.
REMOTE_VERSION_URL = "https://raw.githubusercontent.com/ThiaudioTT/hoi4-presence/main/version.json"


class ManifestError(ValueError):
    """Raised when a version.json is missing or malformed."""


def parseManifest(text: str) -> dict:
    """Parse a version manifest, checking the fields we depend on."""
    try:
        manifest = json.loads(text)
    except json.JSONDecodeError as error:
        raise ManifestError(f"version manifest is not valid JSON: {error}") from error

    if not isinstance(manifest, dict) or "version" not in manifest:
        raise ManifestError("version manifest has no 'version' key")

    try:
        Version(manifest["version"])
    except (ValueError, TypeError) as error:
        # TypeError: a non-string value, e.g. "version": 130 in a hand-edited file.
        raise ManifestError(f"{manifest['version']!r} is not a valid semantic version") from error

    return manifest


def loadLocalVersion(baseDir: str | os.PathLike[str], fileName: str = VERSION_FILE) -> dict:
    """Read and validate the manifest sitting next to the executable."""
    path = Path(baseDir) / fileName
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as error:
        raise ManifestError(f"could not read {path}: {error}") from error
    return parseManifest(text)


def isOutdated(local: str, remote: str) -> bool:
    """Whether ``local`` is an older release than ``remote``.

    Both must be bare semantic versions. GitHub tag names carry a leading ``v``
    and are rejected rather than silently mis-compared.
    """
    return Version(local) < Version(remote)


def shouldAutoUpdate(localManifest: dict, remoteManifest: dict) -> bool:
    """Whether to update: the user allows it and a newer release exists."""
    if not localManifest.get("auto-update"):
        return False
    return isOutdated(localManifest["version"], remoteManifest["version"])
