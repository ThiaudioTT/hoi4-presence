"""The installer's behaviour when the auto-updater is driving it.

Only the headless path is covered here: the rest of ``main()`` moves real files
around a real HOI4 install, and its transforms already live as pure functions in
``hoi4presence.install.steps``.
"""

from __future__ import annotations

import installer
import pytest


@pytest.fixture(autouse=True)
def interactive(monkeypatch):
    """Default every test to the hand-run installer, not the auto-updater."""
    monkeypatch.setattr(installer, "IS_UPDATE", False)


def test_prompt_for_path_asks_the_user_when_run_by_hand(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda prompt="": r"D:\HOI4")

    assert installer.promptForPath("where? ") == r"D:\HOI4"


def test_prompt_for_path_refuses_to_block_an_auto_update(monkeypatch):
    """Regression: the auto-updater handed the real input() to findDocumentsDir.

    It has already stopped the running presence by that point, so a user whose
    documents or game folder is not at the default left setup.exe waiting
    forever on a console nobody was looking at.
    """
    monkeypatch.setattr(installer, "IS_UPDATE", True)

    with pytest.raises(RuntimeError, match="auto-update"):
        installer.promptForPath("where? ")


def test_custom_input_still_skips_the_cosmetic_pauses(monkeypatch):
    monkeypatch.setattr(installer, "IS_UPDATE", True)

    assert installer.customInput("press enter") is None
