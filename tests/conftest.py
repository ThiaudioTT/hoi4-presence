"""Shared fixtures.

Everything here is platform-neutral: the suite runs on Linux CI even though the
product only runs on Windows.
"""

from __future__ import annotations

import ast
import json
import shutil
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = Path(__file__).resolve().parent / "data"


@pytest.fixture(scope="session")
def repoRoot() -> Path:
    return REPO_ROOT


@pytest.fixture(scope="session")
def dataDir() -> Path:
    return DATA_DIR


@pytest.fixture
def saveFile(tmp_path: Path) -> Path:
    """A copy of the sample GER save, in a writable temp directory."""
    target = tmp_path / "GER_1936_01_01_12.hoi4"
    shutil.copy(DATA_DIR / "save_ger_1936.hoi4", target)
    return target


@pytest.fixture
def saveDir(tmp_path: Path) -> Path:
    """A save folder holding three saves at staggered mtimes plus a decoy."""
    folder = tmp_path / "save games"
    folder.mkdir()
    for index, name in enumerate(["oldest.hoi4", "middle.hoi4", "newest.hoi4"]):
        path = folder / name
        path.write_text("HOI4txt\n", encoding="utf-8")
        # Fixed, ordered timestamps so the test does not race the clock.
        import os

        os.utime(path, (1_700_000_000 + index * 60, 1_700_000_000 + index * 60))
    (folder / "notes.txt").write_text("not a save", encoding="utf-8")
    return folder


@pytest.fixture
def scriptedInput():
    """Build an ``input``-like callable that replays canned answers."""

    def build(answers):
        remaining = list(answers)
        calls: list[str] = []

        def fakeInput(prompt: str = "") -> str:
            calls.append(prompt)
            if not remaining:
                raise AssertionError(f"input() called more times than scripted: {prompt!r}")
            return remaining.pop(0)

        fakeInput.calls = calls
        return fakeInput

    return build


@pytest.fixture(scope="session")
def fakeEnv() -> dict[str, str]:
    return {
        "USERPROFILE": r"C:\Users\test",
        "PROGRAMFILES(X86)": r"C:\Program Files (x86)",
        "TEMP": r"C:\Temp",
    }


@pytest.fixture(scope="session")
def countriesSource() -> list[tuple[str, str, str]]:
    """Every ``(tag, name, flag)`` triple as written in countries.py.

    Parsed from the source rather than the imported dict, because Python has
    already silently collapsed any duplicate key by the time the module loads --
    which is exactly the class of bug this data needs guarding against.
    """
    source = (REPO_ROOT / "src" / "hoi4presence" / "countries.py").read_text(encoding="utf-8")
    tree = ast.parse(source)

    for node in ast.walk(tree):
        if isinstance(node, ast.AnnAssign) and getattr(node.target, "id", None) == "countries":
            entries = []
            for keyNode, valueNode in zip(node.value.keys, node.value.values, strict=True):
                tag = ast.literal_eval(keyNode)
                nameNode, flagNode = valueNode.elts
                name = ast.literal_eval(nameNode)
                # The flag is either a string literal or the DEFAULT_LARGE_IMAGE name.
                flag = flagNode.id if isinstance(flagNode, ast.Name) else ast.literal_eval(flagNode)
                entries.append((tag, name, flag))
            return entries

    raise AssertionError("could not find the `countries` dict in countries.py")


@pytest.fixture(scope="session")
def assetKeys() -> set[str]:
    """Lowercased stems of every flag PNG mirrored under assets/initialCountries/.

    Scoped to that folder rather than all of assets/: the ideology and ironman
    badges beside it are keyed off `ideology=`, not off a country tag, so the
    country table cannot account for them and would report them as orphans.
    """
    return {path.stem.lower() for path in (REPO_ROOT / "assets" / "initialCountries").rglob("*.png")}


@pytest.fixture(scope="session")
def releaseAssets() -> list[dict]:
    return json.loads((DATA_DIR / "github_release_assets.json").read_text(encoding="utf-8"))


@pytest.fixture(scope="session")
def buildSpecTargets() -> list[tuple[str, str, bool]]:
    """The ``(script, exeName, console)`` triples declared in build.spec."""
    source = (REPO_ROOT / "build.spec").read_text(encoding="utf-8")
    tree = ast.parse(source)

    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", None) == "TARGETS":
            targets = []
            for element in node.value.elts:
                scriptNode, nameNode, consoleNode = element.elts
                # os.path.join(ENTRYPOINTS, "name.py") -> take the literal leaf.
                scriptName = ast.literal_eval(scriptNode.args[-1])
                targets.append((scriptName, ast.literal_eval(nameNode), ast.literal_eval(consoleNode)))
            return targets

    raise AssertionError("could not find TARGETS in build.spec")
