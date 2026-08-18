"""The launcher shim -- what the Paradox launcher actually spawns.

This used to be a `.bat` file, so none of it was testable. It is the whole
runtime chain in one function: get this wrong and clicking Play does nothing.
"""

from __future__ import annotations

from pathlib import Path

import launcher
import pytest


@pytest.fixture
def spawns(monkeypatch) -> list[tuple[list[str], Path]]:
    """Record every Popen as ``(argv, cwd)`` instead of starting anything."""
    calls: list[tuple[list[str], Path]] = []

    def fakePopen(argv, cwd=None, **kwargs):
        calls.append((list(argv), cwd))
        return None

    monkeypatch.setattr(launcher.subprocess, "Popen", fakePopen)
    return calls


@pytest.fixture
def gameDir(monkeypatch, tmp_path: Path) -> Path:
    """A game folder the shim believes it is running from."""
    folder = tmp_path / "Hearts of Iron IV"
    folder.mkdir()
    monkeypatch.setattr(launcher.sys, "argv", [str(folder / "runRPC.exe")])
    return folder


def writeConfig(gameDir: Path, documents: Path) -> Path:
    """Write runRPC.cfg exactly the way installer.py does."""
    documents.mkdir(parents=True, exist_ok=True)
    (gameDir / launcher.CONFIG_NAME).write_text(str(documents), encoding="utf-8")
    return documents / launcher.INSTALL_DIR_NAME


def test_it_starts_the_game_the_updater_and_the_presence(spawns, gameDir, tmp_path):
    installDir = writeConfig(gameDir, tmp_path / "Documents" / "Hearts of Iron IV")

    assert launcher.main() == 0

    assert [argv for argv, _ in spawns] == [
        [str(gameDir / "hoi4.exe"), "-gdpr-compliant"],
        [str(installDir / "checkupdate.exe")],
        [str(installDir / "hoi4Presence.exe")],
    ]


def test_the_game_starts_first(spawns, gameDir, tmp_path):
    """The old .bat had this ordering by accident; keep it on purpose."""
    writeConfig(gameDir, tmp_path / "Documents" / "Hearts of Iron IV")

    launcher.main()

    assert spawns[0][0][0].endswith("hoi4.exe")


def test_the_game_still_starts_without_a_config(spawns, gameDir):
    """Worst case: a broken install must cost the presence, not the game.

    runRPC.exe is built with console=False, so an exception raised here is
    invisible -- the user would just see the Play button do nothing.
    """
    assert launcher.main() == 0

    assert len(spawns) == 1
    assert spawns[0][0] == [str(gameDir / "hoi4.exe"), "-gdpr-compliant"]


def test_a_documents_path_with_non_ascii_characters_survives(spawns, gameDir, tmp_path):
    """Regression: the .bat was read in the console codepage, not UTF-8.

    Rewriting it as UTF-8 corrupted any non-ASCII character in the path -- and
    the rewrite only ran for custom paths, i.e. exactly the ones likely to have
    them. Both ends are Python now, so the round trip is plain UTF-8.
    """
    installDir = writeConfig(gameDir, tmp_path / "Dokumente" / "Herz der Eisen – über")

    launcher.main()

    assert spawns[-1][0] == [str(installDir / "hoi4Presence.exe")]


def test_the_shim_runs_each_process_in_its_own_folder(spawns, gameDir, tmp_path):
    """`start` left all three in the game folder; give each its own instead.

    Nothing depends on it today -- the payload resolves everything from
    ``getBaseDir()``, which is the executable's folder -- but inheriting the
    game folder is the kind of accident that only shows up once something
    reaches for a relative path.
    """
    installDir = writeConfig(gameDir, tmp_path / "Documents" / "Hearts of Iron IV")

    launcher.main()

    assert [cwd for _, cwd in spawns] == [gameDir, installDir, installDir]
