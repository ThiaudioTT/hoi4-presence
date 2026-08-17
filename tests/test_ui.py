"""The console wizard the three windowed-console executables share.

Everything here drives a :class:`Wizard` over an in-memory console. With a
non-terminal console rich's live display refreshes to nothing, and the progress
bar is transient anyway, so the only thing that lands in the buffer is the
permanent line each finished step prints. That is what the assertions read: no
ANSI, no bar glyphs, nothing that moves when rich changes its rendering.
"""

from __future__ import annotations

import io
import time

import pytest
from rich.console import Console

from hoi4presence.countries import countries
from hoi4presence.paths import findDocumentsDir
from hoi4presence.ui import FLAG_PALETTE, FLAGS, MIN_STEP_SECONDS, Wizard, renderFlag


@pytest.fixture
def wizardFor(scriptedInput):
    """Build a (wizard, output) pair with pacing off and canned answers."""

    def build(answers=(), *, interactive=True, terminal=False, totalSteps=None):
        output = io.StringIO()
        console = Console(file=output, width=80, force_terminal=terminal, no_color=True, highlight=False)
        wizard = Wizard(
            "title",
            "subtitle",
            totalSteps=totalSteps,
            interactive=interactive,
            console=console,
            reader=scriptedInput(answers),
            minStepSeconds=0,
        )
        return wizard, output

    return build


def test_ask_refuses_to_block_an_auto_update(wizardFor):
    """Regression: the auto-updater handed the real input() to findDocumentsDir.

    It has already stopped the running presence by that point, so a user whose
    documents or game folder is not at the default left setup.exe waiting
    forever on a console nobody was looking at.
    """
    wizard, _ = wizardFor(interactive=False)

    with wizard, pytest.raises(RuntimeError, match="auto-update"):
        wizard.ask("where? ")

    assert wizard.reader.calls == [], "an auto-update must not read stdin at all"


def test_ask_and_warn_drive_the_real_path_discovery_loop(wizardFor, tmp_path):
    """The wizard's prompt/log pair is what paths.findDirContaining expects."""
    good = tmp_path / "documents"
    good.mkdir()
    (good / "settings.txt").write_text("save_as_binary=yes", encoding="utf-8")
    wizard, output = wizardFor([str(good)])

    with wizard:
        found = findDocumentsDir(tmp_path / "nowhere", wizard.ask, wizard.warn)

    assert found == good
    # The rejected candidate was reported before the user was asked again.
    assert "nowhere" in output.getvalue()


def test_each_step_leaves_a_line_behind_in_order(wizardFor):
    wizard, output = wizardFor(totalSteps=3)

    with wizard:
        for label in ("first", "second", "third"):
            with wizard.step(label):
                pass

    text = output.getvalue()
    assert text.index("first") < text.index("second") < text.index("third")
    assert text.count(wizard.tick) == 3
    assert wizard.stepNumber == 3


def test_a_failing_step_marks_itself_and_re_raises(wizardFor):
    """A swallowed exception here would report success on a broken install."""
    wizard, output = wizardFor()

    with wizard, pytest.raises(ValueError, match="disk full"):
        with wizard.step("copying the payload"):
            raise ValueError("disk full")

    assert "copying the payload" in output.getvalue()


def test_pacing_is_off_for_an_auto_update(wizardFor):
    """Eight paced steps behind a running game is eight seconds of dead presence."""
    assert Wizard("t", interactive=False).minStepSeconds == 0
    assert Wizard("t", interactive=True).minStepSeconds == MIN_STEP_SECONDS

    output = io.StringIO()
    wizard = Wizard("t", interactive=False, console=Console(file=output), reader=lambda prompt: "")
    started = time.monotonic()
    with wizard:
        for label in ("a", "b", "c"):
            with wizard.step(label):
                pass

    assert time.monotonic() - started < 0.5


def test_a_download_without_a_content_length_stays_indeterminate(wizardFor):
    """A missing Content-Length arrives as total=0.

    As a rich task total that does not mean "unknown", it means "already
    finished" -- the bar would fill green on the very first chunk. Asserted on
    the task rather than the rendered bar so it does not move with rich's output.
    """
    wizard, _ = wizardFor()

    with wizard, wizard.step("downloading") as onProgress:
        onProgress(1000, 0)
        task = wizard._progress.tasks[0]

        assert task.total is None
        assert not task.finished


def test_the_display_is_stopped_even_when_a_step_escapes(wizardFor):
    """Live.start hid the cursor; only stop puts it back."""
    wizard, _ = wizardFor()

    with pytest.raises(ValueError), wizard:
        with wizard.step("boom"):
            raise ValueError("boom")

    assert wizard._progress.live.is_started is False


def test_the_flag_parade_costs_an_auto_update_nothing(wizardFor):
    wizard, output = wizardFor(interactive=False)

    started = time.monotonic()
    with wizard:
        wizard.flagParade(seconds=5)

    assert time.monotonic() - started < 0.5


def test_the_flag_parade_stops_the_progress_bar_first(wizardFor):
    """rich allows one live display at a time, so the bar has to go first."""
    wizard, _ = wizardFor()

    with wizard:
        wizard.flagParade(seconds=0.07)

        assert wizard._progress.live.is_started is False


@pytest.mark.parametrize("tag", sorted(FLAGS))
def test_every_flag_is_well_formed(tag):
    rows = FLAGS[tag]
    widths = {len(row) for row in rows}

    assert len(widths) == 1, f"{tag} has ragged rows: {rows}"
    unknown = {cell for row in rows for cell in row} - set(FLAG_PALETTE)
    assert not unknown, f"{tag} uses colours that are not in FLAG_PALETTE: {sorted(unknown)}"


@pytest.mark.parametrize("tag", sorted(FLAGS))
def test_every_flag_names_a_country_that_exists(tag):
    """getCountry falls back to the tag itself, so a typo would render as "XXX"."""
    assert tag in countries

    assert countries[tag][0] in renderFlag(tag).plain
