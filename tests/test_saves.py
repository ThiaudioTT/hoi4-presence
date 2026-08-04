"""Reading and parsing save headers."""

from __future__ import annotations

import os

import pytest

from hoi4presence.saves import (
    HEADER_LINES,
    SaveHeader,
    SaveParseError,
    findSaves,
    isSaveRecent,
    parseSaveHeader,
    pickLatestSave,
    readSaveHeader,
)

SAMPLE_HEADER = 'HOI4txt\nplayer="GER"\nideology=fascism\ndate="1936.1.1.12"\ndifficulty="normal"\n'


def test_parses_the_sample_save(saveFile):
    header = parseSaveHeader(readSaveHeader(saveFile))

    assert header == SaveHeader(tag="GER", ideology="fascism", date="1936.1.1.12", difficulty="normal")


def test_year_is_the_leading_date_component():
    assert parseSaveHeader(SAMPLE_HEADER).year == "1936"


def test_quotes_and_keys_are_stripped():
    header = parseSaveHeader(SAMPLE_HEADER)

    assert header.tag == "GER"
    assert header.difficulty == "normal"


def test_field_order_does_not_matter():
    reordered = 'HOI4txt\ndifficulty="normal"\ndate="1939.9.1.12"\nplayer="SOV"\nideology=communism\n'

    assert parseSaveHeader(reordered) == SaveHeader("SOV", "communism", "1939.9.1.12", "normal")


def test_an_extra_header_field_does_not_hide_the_last_one(tmp_path):
    """A HOI4 patch inserting a field must not push difficulty out of the window."""
    path = tmp_path / "patched.hoi4"
    path.write_text(SAMPLE_HEADER.replace("player=", "new_field=1\nplayer="), encoding="utf-8")

    assert parseSaveHeader(readSaveHeader(path)).difficulty == "normal"


def test_truncated_header_raises_a_useful_error(dataDir):
    text = readSaveHeader(dataDir / "save_truncated.hoi4")

    with pytest.raises(SaveParseError, match="ideology"):
        parseSaveHeader(text)


def test_binary_save_raises_rather_than_indexerror():
    """A save written with save_as_binary=yes has no readable key=value header."""
    with pytest.raises(SaveParseError):
        parseSaveHeader("HOI4bin\x00\x01\x02garbage")


def test_reads_at_most_the_header_lines(tmp_path):
    path = tmp_path / "long.hoi4"
    path.write_text("\n".join(f"line{n}=x" for n in range(50)), encoding="utf-8")

    assert len(readSaveHeader(path).splitlines()) == HEADER_LINES


def test_reading_a_short_file_does_not_hang(dataDir):
    assert readSaveHeader(dataDir / "save_truncated.hoi4").count("\n") == 2


def test_picks_the_newest_save(saveDir):
    latest = pickLatestSave(findSaves(str(saveDir / "*.hoi4")))

    assert os.path.basename(latest) == "newest.hoi4"


def test_glob_ignores_non_saves(saveDir):
    assert all(path.endswith(".hoi4") for path in findSaves(str(saveDir / "*.hoi4")))


def test_no_saves_returns_none():
    """Regression: max() on an empty glob raised, and the error was swallowed."""
    assert pickLatestSave([]) is None


@pytest.mark.parametrize(
    ("age", "expected"),
    [(0, True), (119, True), (120, True), (121, False), (3600, False), (-5, True)],
)
def test_freshness_window(age, expected):
    now = 1_700_000_000

    assert isSaveRecent(now - age, now) is expected
