"""The presence loop's connection lifecycle.

``runner`` is the one module that imports :mod:`pypresence` and :mod:`psutil`,
which CI deliberately does not install, so both are stubbed into ``sys.modules``
before it is imported. That keeps the suite Linux-clean while still covering the
reconnect logic -- the only part of the loop with real branching, and the part
that decides whether a user sees a presence at all.
"""

from __future__ import annotations

import sys
import types

import pytest

from hoi4presence.saves import SaveHeader, SaveParseError

HEADER = SaveHeader(tag="GER", ideology="fascism", date="1936.1.1.12", difficulty="normal")


class FakePresence:
    """Stand-in for ``pypresence.Presence``, scripted to fail on demand."""

    instances: list[FakePresence] = []
    connectFailures = 0
    updateFailures = 0

    def __init__(self, clientId: str) -> None:
        self.clientId = clientId
        self.connected = False
        self.closed = False
        self.updates: list[dict] = []
        FakePresence.instances.append(self)

    def connect(self) -> None:
        if FakePresence.connectFailures > 0:
            FakePresence.connectFailures -= 1
            raise ConnectionRefusedError("Discord is not running")
        self.connected = True

    def update(self, **payload) -> None:
        if FakePresence.updateFailures > 0:
            FakePresence.updateFailures -= 1
            raise BrokenPipeError("the Discord pipe is closed")
        self.updates.append(payload)

    def close(self) -> None:
        self.closed = True


@pytest.fixture
def runner(monkeypatch):
    """Import ``hoi4presence.runner`` against stubbed Windows-only packages."""
    FakePresence.instances = []
    FakePresence.connectFailures = 0
    FakePresence.updateFailures = 0

    pypresence = types.ModuleType("pypresence")
    pypresence.Presence = FakePresence

    psutil = types.ModuleType("psutil")
    psutil.NoSuchProcess = type("NoSuchProcess", (Exception,), {})
    psutil.AccessDenied = type("AccessDenied", (Exception,), {})
    psutil.process_iter = lambda attrs=None: []

    monkeypatch.setitem(sys.modules, "pypresence", pypresence)
    monkeypatch.setitem(sys.modules, "psutil", psutil)
    sys.modules.pop("hoi4presence.runner", None)

    import hoi4presence.runner as module

    monkeypatch.setattr(module.time, "sleep", lambda seconds: None)
    yield module

    sys.modules.pop("hoi4presence.runner", None)


def runCycles(runner, monkeypatch, cycles: int) -> None:
    """Report the game as running for ``cycles`` polls, then as closed."""
    remaining = iter([True] * (cycles - 1) + [False])
    monkeypatch.setattr(runner, "isGameRunning", lambda *args, **kwargs: next(remaining))


def test_connects_and_publishes_the_idle_payload(runner, monkeypatch):
    runCycles(runner, monkeypatch, 1)
    monkeypatch.setattr(runner, "readCurrentSave", lambda pattern, now: None)

    assert runner.run("*.hoi4") == 0

    connection = FakePresence.instances[0]
    assert connection.connected
    assert connection.updates[0]["details"] == "Preparing for war..."


def test_the_connection_is_closed_when_the_game_exits(runner, monkeypatch):
    runCycles(runner, monkeypatch, 1)
    monkeypatch.setattr(runner, "readCurrentSave", lambda pattern, now: None)

    runner.run("*.hoi4")

    assert FakePresence.instances[0].closed


def test_discord_being_down_at_launch_is_retried_rather_than_fatal(runner, monkeypatch):
    """Regression: the presence used to give up for the whole session."""
    FakePresence.connectFailures = 1
    runCycles(runner, monkeypatch, 2)
    monkeypatch.setattr(runner, "readCurrentSave", lambda pattern, now: (HEADER, "GER.hoi4"))

    assert runner.run("*.hoi4") == 0

    assert len(FakePresence.instances) == 2
    assert FakePresence.instances[1].connected
    assert any(update["details"] == "Playing as German Reich" for update in FakePresence.instances[1].updates)


def test_a_dead_pipe_is_dropped_so_the_next_cycle_reconnects(runner, monkeypatch):
    """Regression: a Discord restart left the loop writing to a dead socket."""
    FakePresence.updateFailures = 1
    runCycles(runner, monkeypatch, 2)
    monkeypatch.setattr(runner, "readCurrentSave", lambda pattern, now: None)

    runner.run("*.hoi4")

    assert len(FakePresence.instances) == 2
    assert FakePresence.instances[0].closed
    assert FakePresence.instances[1].connected


def test_an_unreadable_save_does_not_drop_the_discord_connection(runner, monkeypatch):
    """A binary save is a save problem; reconnecting to Discord would not help."""
    runCycles(runner, monkeypatch, 3)

    def raiseParseError(pattern, now):
        raise SaveParseError("save_as_binary=yes")

    monkeypatch.setattr(runner, "readCurrentSave", raiseParseError)

    runner.run("*.hoi4")

    assert len(FakePresence.instances) == 1


def test_the_game_process_is_matched_by_its_prefetched_name(runner, monkeypatch):
    """process_iter(["name"]) prefetches into .info; calling .name() re-reads it."""

    class FakeProcess:
        def __init__(self, name):
            self.info = {"name": name}

    processes = [FakeProcess("explorer.exe"), FakeProcess("hoi4.exe")]
    monkeypatch.setattr(runner.psutil, "process_iter", lambda attrs=None: processes)

    assert runner.isGameRunning() is True
    assert runner.isGameRunning("notepad.exe") is False
