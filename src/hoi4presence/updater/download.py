"""Downloading and unpacking a published release from GitHub."""

from __future__ import annotations

import logging
import os
import shutil
from collections.abc import Callable

import requests

from hoi4presence.updater.release import assetName, pickReleaseAsset

logger = logging.getLogger(__name__)

# Fetched by tag rather than through /releases/latest. The version that triggers
# an update comes from version.json on main, and /releases/latest can resolve to
# a different release -- a rolling prerelease such as "beta", or the
# previous stable one while the new tag has not been pushed yet. Downloading that
# reinstalls the version the user already has, on every single launch.
RELEASE_BY_TAG_URL = "https://api.github.com/repos/ThiaudioTT/hoi4-presence/releases/tags/{tagName}"

CHUNK_SIZE = 1024**2


def downloadUpdate(
    tagName: str,
    destination: str | None = None,
    *,
    onProgress: Callable[[int, int], None] | None = None,
) -> str | None:
    """Download and unpack the release published as ``tagName``.

    Returns the directory it was unpacked into, or None when there is nothing to
    install or the download failed. ``onProgress`` is called with the bytes so
    far and the total from the Content-Length header, which servers may omit and
    which then arrives as 0.
    """
    try:
        # Inside the try: a missing TEMP is a failed update, not a traceback.
        destination = destination or os.environ["TEMP"]

        release = requests.get(RELEASE_BY_TAG_URL.format(tagName=tagName), timeout=30)
        if release.status_code == 404:
            # version.json on main is bumped when the branch merges; the tag is
            # pushed afterwards. Between the two there is simply nothing to get.
            logger.info("No release tagged %s has been published yet; nothing to install.", tagName)
            return None
        # Without this, a rate-limited 403 body is parsed as a release and fails
        # later as an unexplained KeyError.
        release.raise_for_status()

        downloadLink = pickReleaseAsset(release.json().get("assets", []), tagName)
        if downloadLink is None:
            logger.info("Release %s has no asset named %s; nothing to install.", tagName, assetName(tagName))
            return None

        archivePath = os.path.join(destination, assetName(tagName))
        logger.info("Downloading %s", downloadLink)

        with requests.get(downloadLink, allow_redirects=True, stream=True, timeout=60) as response:
            response.raise_for_status()
            # Read the size from the header; reading .content here would pull the
            # whole body into memory and leave nothing for iter_content.
            total = int(response.headers.get("content-length", 0))
            downloaded = 0
            with open(archivePath, "wb") as handle:
                for chunk in response.iter_content(CHUNK_SIZE):
                    handle.write(chunk)
                    downloaded += len(chunk)
                    if onProgress is not None:
                        onProgress(downloaded, total)

        logger.info("Download complete.")

        extractedPath = os.path.join(destination, f"hoi4-presence-{tagName}")
        shutil.unpack_archive(archivePath, extractedPath)
        os.remove(archivePath)
        return extractedPath

    except Exception:
        logger.exception("Update failed; starting the current version instead.")
        return None
