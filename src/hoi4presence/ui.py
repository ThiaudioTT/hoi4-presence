"""The console UI shared by setup.exe, uninstall.exe and checkupdate.exe.

These three are built with a console window, and their output *is* the user
interface. Left as bare ``print`` the whole install finished faster than anyone
could read it, so :class:`Wizard` gives every stage a progress bar and holds it
on screen for at least :data:`MIN_STEP_SECONDS`.

The two windowed executables must never import this module: they are built
``console=False``, so ``sys.stdout`` is None and rich would render into a void.
``tests/test_packaging.py`` enforces that.
"""

from __future__ import annotations

import time
from collections.abc import Callable, Iterator
from contextlib import contextmanager

from rich.console import Console, Group
from rich.live import Live
from rich.panel import Panel
from rich.progress import BarColumn, DownloadColumn, Progress, SpinnerColumn, Task, TaskID, TextColumn
from rich.text import Text

from hoi4presence.countries import getCountry

# How long a step stays on screen at minimum. Every real step here -- a JSON
# edit, copying four files -- finishes in milliseconds, so without this the user
# sees a window flash and nothing else.
MIN_STEP_SECONDS = 1.2
# Sleeps used to fill a paced bar. 24 over 1.2s is ~20fps, which reads as smooth.
PACE_FRAMES = 24

FLAG_PARADE_SECONDS = 3.0
# One character per cell, expanded FLAG_CELL_WIDTH columns wide.
FLAG_CELL_WIDTH = 3

# A grid rather than horizontal bands, so vertical tricolours and the Japanese
# sun come out of the same renderer.
FLAG_PALETTE = {
    "k": "black",
    "w": "white",
    "r": "red",
    "b": "blue",
    "y": "yellow",
    "g": "green",
}

# The majors, as three rows of FLAG_PALETTE keys. Three rows of colour cannot
# carry an emblem, so these are the colours only: GER is the plain
# black-white-red tricolour, SOV is solid red without the hammer and sickle, USA
# has no canton. That is the limit of the medium, not an oversight.
FLAGS: dict[str, tuple[str, ...]] = {
    "GER": ("kkkkk", "wwwww", "rrrrr"),
    "SOV": ("rrrrr", "rrrrr", "rrrrr"),
    "USA": ("rrrrr", "wwwww", "rrrrr"),
    "ENG": ("brwrb", "rrwrr", "brwrb"),
    "FRA": ("bbwwr", "bbwwr", "bbwwr"),
    "ITA": ("ggwwr", "ggwwr", "ggwwr"),
    "JAP": ("wwwww", "wwrww", "wwwww"),
}


class BytesColumn(DownloadColumn):
    """A byte counter for tasks that really are a download, and blank for the rest.

    Progress applies its columns to every task, and the plain DownloadColumn
    reads any total as a byte count -- so the overall bar announced "1/3 bytes"
    and a paced step counted up to "95/100 bytes".
    """

    def render(self, task: Task) -> Text:
        if not task.fields.get("isDownload"):
            return Text("")
        return super().render(task)


def renderFlag(tag: str) -> Text:
    """Draw one country's flag as coloured blocks, with its tag and name beside it."""
    name = getCountry(tag).name
    labels = ["", f"  {tag}", f"  {name}"]

    flag = Text()
    for row, label in zip(FLAGS[tag], labels, strict=True):
        for cell in row:
            flag.append(" " * FLAG_CELL_WIDTH, style=f"on {FLAG_PALETTE[cell]}")
        flag.append(label)
        flag.append("\n")
    return flag


class Wizard:
    """A console wizard: a banner, a paced progress bar per step, and prompts.

    ``interactive`` is the one switch that matters. An auto-update runs
    ``setup.exe -update`` behind the game the user is already playing, on a
    console nobody is looking at, so it must never pause for a keypress and must
    never pace a step -- eight steps of deliberate sleeping there is eight
    seconds with no Discord presence, for an audience of nobody.
    """

    def __init__(
        self,
        title: str,
        subtitle: str = "",
        *,
        totalSteps: int | None = None,
        interactive: bool = True,
        console: Console | None = None,
        reader: Callable[[str], str] = input,
        minStepSeconds: float | None = None,
    ) -> None:
        self.title = title
        self.subtitle = subtitle
        self.interactive = interactive
        # highlight=False: rich's ReprHighlighter otherwise colours fragments of
        # `C:\Users\...` and `save_as_binary=no`, which reads as corruption.
        self.console = console if console is not None else Console(highlight=False)
        self.reader = reader
        self.minStepSeconds = MIN_STEP_SECONDS if minStepSeconds is None else minStepSeconds
        if not interactive:
            self.minStepSeconds = 0.0

        # Our own glyphs, unlike rich's boxes and bars, get no automatic
        # substitution. legacy_windows is the raster-font risk and ascii_only the
        # codepage one; they are independent, so check both.
        plain = self.console.legacy_windows or self.console.options.ascii_only
        self.tick, self.cross = ("+", "x") if plain else ("\u2713", "\u2717")

        self.stepNumber = 0
        self._progress = Progress(
            # "line" rather than the default "dots": those are braille, and rich
            # has no ASCII fallback for a spinner.
            SpinnerColumn("line"),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(bar_width=32),
            BytesColumn(),
            console=self.console,
            # Erased on stop, so ask()'s stop/start leaves no dead bars behind.
            transient=True,
            # Nothing here uses bare print, so the redirect buys nothing and
            # swapping sys.stdout only creates hazards -- see logging_setup.
            redirect_stdout=False,
            redirect_stderr=False,
        )
        self._overall: TaskID | None = None
        if totalSteps:
            self._overall = self._progress.add_task(f"[dim]Step 0 of {totalSteps}", total=totalSteps)
        self.totalSteps = totalSteps

    def __enter__(self) -> Wizard:
        self.console.print(Panel(self.subtitle or self.title, title=self.title, padding=(1, 2)))
        self._progress.start()
        return self

    def __exit__(self, *exc: object) -> None:
        # Live.start hid the cursor and only stop restores it, so this has to run
        # even when a step raises all the way out to the PyInstaller bootloader.
        self._progress.stop()

    @contextmanager
    def step(self, label: str) -> Iterator[Callable[[int, int], None]]:
        """Run a stage behind a progress bar, and leave a permanent line for it.

        Yields an ``onProgress(done, total)`` callback. Ignore it and the bar
        pulses for however long the work takes, then fills over whatever is left
        of ``minStepSeconds``. Call it and the bar tracks real bytes instead.
        """
        self.stepNumber += 1
        taskId = self._progress.add_task(f"{self.stepNumber}. {label}", total=None)
        determinate = False
        started = time.monotonic()

        def onProgress(done: int, total: int) -> None:
            nonlocal determinate
            determinate = True
            # `total or None`: a server may omit Content-Length and total arrives
            # as 0. As a task total that does not mean "unknown", it means
            # "already finished", and the bar fills green on the first chunk.
            self._progress.update(taskId, completed=done, total=total or None, isDownload=True)

        try:
            yield onProgress
        except Exception:
            self._finishRow(taskId, f"  [red]{self.cross}[/red] {label}")
            raise
        else:
            if not determinate:
                self._pace(taskId, time.monotonic() - started)
            self._finishRow(taskId, f"  [green]{self.tick}[/green] {label}")
            if self._overall is not None:
                self._progress.update(
                    self._overall,
                    completed=self.stepNumber,
                    description=f"[dim]Step {self.stepNumber} of {self.totalSteps}",
                )

    def warn(self, reason: str) -> None:
        """Report why a candidate path was rejected. Plugs into findDirContaining."""
        self.console.print(f"  [yellow]![/yellow] {reason}")

    def ask(self, question: str) -> str:
        """Ask the user for a path. Plugs into findDirContaining as ``prompt``.

        Refusing to read during an auto-update is the point: setup.exe has
        already stopped the running presence by the time it looks for a folder,
        so a user whose install is not at the default used to leave it waiting
        forever on a console nobody was looking at.
        """
        if not self.interactive:
            raise RuntimeError("Cannot ask for a folder during an auto-update.")
        # A live display and input() do not coexist -- the refresh thread redraws
        # over whatever is being typed. Live start/stop is not latched, so this
        # can happen as often as the retry loop needs it.
        self._progress.stop()
        try:
            return self.reader(f"  {question}")
        finally:
            self._progress.start()

    def flagParade(self, seconds: float = FLAG_PARADE_SECONDS) -> None:
        """Cycle the majors' flags, as a full stop after a successful install."""
        if not self.interactive:
            return
        # rich allows only one live display at a time, so the progress bar has to
        # go first. Nothing restarts it: every step is finished by now.
        self._progress.stop()

        pause = seconds / len(FLAGS)
        with Live(console=self.console, transient=True) as live:
            for tag in FLAGS:
                # refresh=True, or Live's 4Hz background thread decides which
                # frames it got round to: a flag held for less than 250ms is
                # replaced before it is ever drawn.
                live.update(Group(Text(), renderFlag(tag)), refresh=True)
                time.sleep(pause)

    def finish(self, *lines: str) -> None:
        """Show the closing panel, and hold the window open for the user."""
        self._progress.stop()
        self.console.print(Panel(Group(*[Text(line) for line in lines]), title=self.title, padding=(1, 2)))
        if self.interactive:
            self.reader("  Press Enter to close...")

    def fail(self, message: str) -> int:
        """Report a failure and return the exit code, so `return wizard.fail(...)` reads."""
        self._progress.stop()
        self.console.print(Panel(Text(message), title="Failed", border_style="red", padding=(1, 2)))
        if self.interactive:
            self.reader("  Press Enter to close...")
        return 1

    def _finishRow(self, taskId: TaskID, line: str) -> None:
        self._progress.remove_task(taskId)
        # remove_task is the one Progress mutator that does not refresh, and
        # console.print runs the live render hook -- so without this the row we
        # just deleted gets redrawn *below* the permanent line.
        self._progress.refresh()
        self.console.print(line)

    def _pace(self, taskId: TaskID, elapsed: float) -> None:
        """Fill a bar over whatever is left of minStepSeconds."""
        self._progress.update(taskId, total=100, completed=0)
        remaining = self.minStepSeconds - elapsed
        if remaining <= 0:
            # Work that outran the pacing budget, e.g. copying a large payload.
            self._progress.update(taskId, completed=100)
            return
        for frame in range(1, PACE_FRAMES + 1):
            time.sleep(remaining / PACE_FRAMES)
            self._progress.update(taskId, completed=frame * 100 / PACE_FRAMES)
