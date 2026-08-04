"""Downloading and unpacking the latest release from GitHub."""

from __future__ import annotations

import logging
import os
import shutil

import requests

from hoi4presence.updater.release import assetName, formatProgress, pickReleaseAsset

logger = logging.getLogger(__name__)

LATEST_RELEASE_URL = "https://api.github.com/repos/ThiaudioTT/hoi4-presence/releases/latest"

CHUNK_SIZE = 1024**2


def downloadUpdate(destination: str | None = None) -> str | None:
    """Download and unpack the newest release.

    Returns the directory it was unpacked into, or None when there is nothing to
    install or the download failed.
    """
    destination = destination or os.environ["TEMP"]

    try:
        release = requests.get(LATEST_RELEASE_URL, timeout=30).json()
        tagName = release["tag_name"]

        assets = requests.get(
            release["assets_url"],
            headers={"accept": "application/vnd.github+json"},
            timeout=30,
        ).json()

        downloadLink = pickReleaseAsset(assets, tagName)
        if downloadLink is None:
            # Happens whenever /releases/latest resolves to a rolling prerelease
            # tag such as "development", whose asset name never matches.
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
                    logger.info("Downloading... %s", formatProgress(downloaded, total))

        logger.info("Download complete.")

        extractedPath = os.path.join(destination, f"hoi4-presence-{tagName}")
        shutil.unpack_archive(archivePath, extractedPath)
        return extractedPath

    except Exception:
        logger.exception("Update failed; starting the current version instead.")
        return None
