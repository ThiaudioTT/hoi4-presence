"""Base-directory resolution and interactive directory discovery."""

from __future__ import annotations

from pathlib import Path

import pytest

from hoi4presence.paths import (
    SETTINGS_FILE,
    defaultDocumentsDir,
    defaultGameDir,
    findDocumentsDir,
    findGameDir,
    getBaseDir,
    getSavePath,
)


def test_base_dir_when_frozen_is_next_to_the_executable(monkeypatch, tmp_path):
    monkeypatch.setattr("sys.frozen", True, raising=False)
    monkeypatch.setattr("sys.executable", str(tmp_path / "hoi4Presence.exe"))

    assert getBaseDir() == tmp_path


def test_base_dir_from_source_is_next_to_the_script(monkeypatch, tmp_path):
    monkeypatch.delattr("sys.frozen", raising=False)
    script = tmp_path / "hoi4RPC.py"

    assert getBaseDir(script) == tmp_path


def test_save_path_is_a_sibling_save_games_glob(tmp_path):
    parts = Path(getSavePath(tmp_path / "hoi4Presence")).parts

    assert parts[-2:] == ("save games", "*.hoi4")


def test_default_documents_dir_reads_the_given_environment(fakeEnv):
    parts = defaultDocumentsDir(fakeEnv).parts

    assert parts[-3:] == ("Documents", "Paradox Interactive", "Hearts of Iron IV")


def test_default_game_dir_reads_the_given_environment(fakeEnv):
    parts = defaultGameDir(fakeEnv).parts

    assert parts[-3:] == ("steamapps", "common", "Hearts of Iron IV")


def test_windows_env_is_not_read_at_import_time(monkeypatch):
    """The suite must import cleanly on Linux, where these keys do not exist."""
    monkeypatch.delenv("USERPROFILE", raising=False)
    monkeypatch.delenv("PROGRAMFILES(X86)", raising=False)

    import importlib

    import hoi4presence.paths

    importlib.reload(hoi4presence.paths)  # must not raise


def test_directory_with_the_marker_is_accepted_without_prompting(tmp_path, scriptedInput):
    (tmp_path / SETTINGS_FILE).write_text("", encoding="utf-8")
    prompt = scriptedInput([])

    assert findDocumentsDir(tmp_path, prompt) == tmp_path
    assert prompt.calls == []


def test_reprompts_until_a_valid_directory_is_given(tmp_path, scriptedInput):
    good = tmp_path / "good"
    good.mkdir()
    (good / SETTINGS_FILE).write_text("", encoding="utf-8")

    wrong = tmp_path / "wrong"
    wrong.mkdir()  # exists, but has no settings.txt

    prompt = scriptedInput([str(wrong), str(good)])

    assert findDocumentsDir(tmp_path / "missing", prompt) == good
    assert len(prompt.calls) == 2


def test_a_missing_directory_is_described_differently_from_a_missing_marker(tmp_path, scriptedInput):
    good = tmp_path / "good"
    good.mkdir()
    (good / SETTINGS_FILE).write_text("", encoding="utf-8")

    prompt = scriptedInput([str(good)])
    findDocumentsDir(tmp_path / "nope", prompt)

    assert "documents path" in prompt.calls[0]


def test_a_present_directory_missing_its_marker_names_the_marker(tmp_path, scriptedInput):
    good = tmp_path / "good"
    good.mkdir()
    (good / SETTINGS_FILE).write_text("", encoding="utf-8")

    empty = tmp_path / "empty"
    empty.mkdir()

    prompt = scriptedInput([str(good)])
    findDocumentsDir(empty, prompt)

    assert SETTINGS_FILE in prompt.calls[0]


def test_game_dir_is_recognised_by_the_game_executable(tmp_path, scriptedInput):
    (tmp_path / "hoi4.exe").write_text("", encoding="utf-8")

    assert findGameDir(tmp_path, scriptedInput([])) == tmp_path


def test_rejections_are_reported_to_the_log_callback(tmp_path, scriptedInput):
    good = tmp_path / "good"
    good.mkdir()
    (good / SETTINGS_FILE).write_text("", encoding="utf-8")

    messages: list[str] = []
    findDocumentsDir(tmp_path / "nope", scriptedInput([str(good)]), messages.append)

    assert messages and "nope" in messages[0]


def test_missing_windows_env_raises_a_keyerror(monkeypatch):
    monkeypatch.delenv("USERPROFILE", raising=False)

    with pytest.raises(KeyError):
        defaultDocumentsDir()
