"""Naming and progress helpers for GitHub releases.

Standard library only, so the test suite does not need :mod:`requests`.
"""

from __future__ import annotations

# build.spec names the artifact hoi4-presence-v<version>.zip, so a release tag
# must be exactly "v<version>" for this to match. See AGENTS.md.
ASSET_NAME_TEMPLATE = "hoi4-presence-{tagName}.zip"


def assetName(tagName: str) -> str:
    """Name of the release asset published for ``tagName``."""
    return ASSET_NAME_TEMPLATE.format(tagName=tagName)


def pickReleaseAsset(assets: list[dict], tagName: str) -> str | None:
    """Return the download URL of the asset for ``tagName``, or None.

    Returning None rather than falling through matters: the caller used to hand
    the missing path straight to ``shutil.unpack_archive``, so "no asset" and
    "download broke" looked identical.
    """
    wanted = assetName(tagName)
    for asset in assets:
        if asset.get("name") == wanted:
            return asset.get("browser_download_url")
    return None


def formatProgress(downloaded: int, total: int) -> str:
    """Human-readable download progress.

    ``total`` comes from a Content-Length header that servers may omit, so the
    unknown case is reported rather than raising ZeroDivisionError.
    """
    if total <= 0:
        return "?%"
    return f"{downloaded / total * 100:.0f}%"
