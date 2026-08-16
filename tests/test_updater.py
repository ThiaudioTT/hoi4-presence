"""Version comparison and release-asset selection."""

from __future__ import annotations

import json

import pytest

from hoi4presence.updater.release import assetName, formatProgress, pickReleaseAsset
from hoi4presence.updater.version_check import (
    ManifestError,
    isOutdated,
    loadLocalVersion,
    parseManifest,
    shouldAutoUpdate,
)


@pytest.mark.parametrize(
    ("local", "remote", "expected"),
    [
        ("1.2.0", "1.3.0", True),
        ("1.3.0", "1.3.0", False),
        ("1.4.0", "1.3.0", False),
        ("1.3.0", "1.3.1", True),
        ("1.3.0-rc1", "1.3.0", True),
    ],
)
def test_is_outdated(local, remote, expected):
    assert isOutdated(local, remote) is expected


def test_a_leading_v_is_rejected():
    """GitHub tag names carry a "v"; comparing one as a version must not pass silently."""
    with pytest.raises(ValueError):
        isOutdated("v1.3.0", "1.3.0")


def test_manifest_requires_a_version():
    with pytest.raises(ManifestError, match="version"):
        parseManifest('{"auto-update": true}')


def test_manifest_rejects_a_bad_version():
    with pytest.raises(ManifestError):
        parseManifest('{"version": "not-a-version"}')


def test_manifest_rejects_a_non_string_version():
    """Regression: Version(130) raises TypeError, which escaped ManifestError."""
    with pytest.raises(ManifestError):
        parseManifest('{"version": 130}')


def test_manifest_rejects_invalid_json():
    with pytest.raises(ManifestError, match="JSON"):
        parseManifest("{nope}")


def test_auto_update_can_be_turned_off():
    local = {"version": "1.0.0", "auto-update": False}
    remote = {"version": "9.9.9"}

    assert shouldAutoUpdate(local, remote) is False


def test_auto_update_when_outdated_and_allowed():
    assert shouldAutoUpdate({"version": "1.0.0", "auto-update": True}, {"version": "1.3.0"}) is True


def test_no_update_when_current():
    assert shouldAutoUpdate({"version": "1.3.0", "auto-update": True}, {"version": "1.3.0"}) is False


def test_local_version_is_read_from_disk(tmp_path):
    (tmp_path / "version.json").write_text('{"version": "1.2.3", "auto-update": true}', encoding="utf-8")

    assert loadLocalVersion(tmp_path)["version"] == "1.2.3"


def test_a_missing_version_file_is_reported_clearly(tmp_path):
    with pytest.raises(ManifestError, match="could not read"):
        loadLocalVersion(tmp_path)


def test_asset_name_matches_the_build_output():
    assert assetName("v1.3.0") == "hoi4-presence-v1.3.0.zip"


def test_picks_the_matching_asset(releaseAssets):
    url = pickReleaseAsset(releaseAssets, "v1.3.0")

    assert url.endswith("/hoi4-presence-v1.3.0.zip")


def test_similar_asset_names_are_not_matched(releaseAssets):
    """Checksums and near-miss versions must not be mistaken for the release."""
    url = pickReleaseAsset(releaseAssets, "v1.3.0")

    assert "sha256" not in url
    assert "1.30" not in url


def test_no_matching_asset_returns_none(releaseAssets):
    """Regression: a missing asset used to reach shutil.unpack_archive(None, ...)."""
    assert pickReleaseAsset(releaseAssets, "beta") is None


def test_no_assets_at_all_returns_none():
    assert pickReleaseAsset([], "v1.3.0") is None


@pytest.mark.parametrize(
    ("downloaded", "total", "expected"),
    [(0, 100, "0%"), (50, 100, "50%"), (100, 100, "100%"), (7, 9, "78%")],
)
def test_progress_percentages(downloaded, total, expected):
    assert formatProgress(downloaded, total) == expected


@pytest.mark.parametrize("total", [0, -1])
def test_unknown_total_does_not_divide_by_zero(total):
    """Regression: a missing Content-Length used to raise ZeroDivisionError."""
    assert formatProgress(10, total) == "?%"


def test_the_shipped_version_file_is_valid(repoRoot):
    """A bad version bump should fail CI, not every user's updater."""
    manifest = parseManifest((repoRoot / "version.json").read_text(encoding="utf-8"))

    assert isinstance(manifest["auto-update"], bool)


def test_the_shipped_version_file_has_no_leftover_dev_keys(repoRoot):
    manifest = json.loads((repoRoot / "version.json").read_text(encoding="utf-8"))

    assert set(manifest) == {"version", "auto-update"}
