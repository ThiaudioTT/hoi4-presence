"""The edits the installer makes to a user's HOI4 install."""

from __future__ import annotations

import json

import pytest

from hoi4presence.install.steps import (
    BINARY_SAVES_OFF,
    BINARY_SAVES_ON,
    REQUIRED_DIST_FILES,
    findMissingFiles,
    isUpdateMode,
    rewriteBatchDocumentsPath,
    setBinarySaves,
    setLauncherExe,
)


@pytest.mark.parametrize(
    ("argv", "expected"),
    [
        (["setup.exe", "-update"], True),
        (["setup.exe"], False),
        (["setup.exe", "-Update"], False),
        ([], False),
    ],
)
def test_update_mode_detection(argv, expected):
    assert isUpdateMode(argv) is expected


def test_a_missing_required_file_is_detected():
    """Regression: the old check could not detect a missing file at all."""
    present = [name for name in REQUIRED_DIST_FILES if name != "hoi4Presence.exe"]

    assert findMissingFiles(present) == ["hoi4Presence.exe"]


def test_extra_files_are_not_reported_as_missing():
    """Regression: the old check aborted the install on any unexpected file."""
    present = [*REQUIRED_DIST_FILES, "hoi4Presence.log", "readme.txt"]

    assert findMissingFiles(present) == []


def test_a_complete_payload_reports_nothing():
    assert findMissingFiles(REQUIRED_DIST_FILES) == []


def test_an_empty_payload_reports_everything():
    assert findMissingFiles([]) == list(REQUIRED_DIST_FILES)


def test_binary_saves_are_turned_off_for_the_presence(dataDir):
    settings = dataDir.joinpath("settings.txt").read_text(encoding="utf-8")

    assert BINARY_SAVES_OFF in setBinarySaves(settings, enabled=False)


def test_binary_saves_are_restored_on_uninstall(dataDir):
    settings = dataDir.joinpath("settings.txt").read_text(encoding="utf-8")
    disabled = setBinarySaves(settings, enabled=False)

    assert setBinarySaves(disabled, enabled=True) == settings


def test_toggling_is_idempotent(dataDir):
    settings = dataDir.joinpath("settings.txt").read_text(encoding="utf-8")
    once = setBinarySaves(settings, enabled=False)

    assert setBinarySaves(once, enabled=False) == once


def test_only_the_binary_saves_line_changes(dataDir):
    settings = dataDir.joinpath("settings.txt").read_text(encoding="utf-8")
    changed = setBinarySaves(settings, enabled=False)

    differing = [
        (before, after)
        for before, after in zip(settings.splitlines(), changed.splitlines(), strict=True)
        if before != after
    ]

    assert differing == [(BINARY_SAVES_ON, BINARY_SAVES_OFF)]


def test_settings_without_the_key_are_left_alone():
    settings = 'language="l_english"\nautosave=monthly\n'

    assert setBinarySaves(settings, enabled=False) == settings


def test_launcher_points_at_the_shim_after_install(dataDir):
    launcher = json.loads(dataDir.joinpath("launcher-settings.json").read_text(encoding="utf-8"))

    patched = setLauncherExe(launcher, install=True)

    assert patched["exePath"] == "./runRPC.exe"
    assert patched["exeArgs"] == []


def test_launcher_points_back_at_the_game_after_uninstall(dataDir):
    launcher = json.loads(dataDir.joinpath("launcher-settings.json").read_text(encoding="utf-8"))

    patched = setLauncherExe(launcher, install=False)

    assert patched["exePath"] == "./hoi4.exe"
    assert patched["exeArgs"] == ["-gdpr-compliant"]


def test_unrelated_launcher_settings_survive(dataDir):
    launcher = json.loads(dataDir.joinpath("launcher-settings.json").read_text(encoding="utf-8"))

    patched = setLauncherExe(launcher, install=True)

    for key, value in launcher.items():
        if key not in ("exePath", "exeArgs"):
            assert patched[key] == value


def test_patching_the_launcher_does_not_mutate_the_input(dataDir):
    launcher = json.loads(dataDir.joinpath("launcher-settings.json").read_text(encoding="utf-8"))

    setLauncherExe(launcher, install=True)

    assert launcher["exePath"] == "./hoi4.exe"


def test_install_then_uninstall_restores_the_launcher(dataDir):
    launcher = json.loads(dataDir.joinpath("launcher-settings.json").read_text(encoding="utf-8"))

    assert setLauncherExe(setLauncherExe(launcher, install=True), install=False) == launcher


def test_the_batch_documents_path_is_rewritten():
    lines = ['set "documentsPath=C:\\old"\n', "echo hello\n", "exit\n"]

    rewritten = rewriteBatchDocumentsPath(lines, "D:\\Games\\HOI4")

    assert rewritten[0] == 'set "documentsPath=D:\\Games\\HOI4"\n'
    assert rewritten[1:] == lines[1:]


def test_rewriting_an_empty_batch_file_raises():
    with pytest.raises(ValueError):
        rewriteBatchDocumentsPath([], "D:\\Games")
