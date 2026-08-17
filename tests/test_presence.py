"""The payloads handed to Discord."""

from __future__ import annotations

from dataclasses import replace

import pytest

from hoi4presence.countries import DEFAULT_LARGE_IMAGE, getCountry
from hoi4presence.presence import (
    IRONMAN_IMAGE,
    LOGO_IMAGE,
    UNKNOWN_IDEOLOGY_IMAGE,
    buildIdlePresence,
    buildPresence,
)
from hoi4presence.saves import SaveHeader, parseSaveHeader, readSaveHeader

VERSION = "Operation Postern v1.19.2.0.a729 (d245)"
HEADER = SaveHeader(
    tag="GER",
    ideology="fascism",
    date="1936.1.1.12",
    difficulty="normal",
    version=VERSION,
)
START = 1_700_000_000.0


def payloadFor(**overrides) -> dict:
    """A payload for HEADER with some of its fields replaced."""
    header = replace(HEADER, **overrides)
    return buildPresence(getCountry(header.tag), header, START)


def test_payload_for_a_known_country():
    assert buildPresence(getCountry("GER"), HEADER, START) == {
        "state": "1 Jan 1936 · Regular",
        "details": "German Reich — Fascist",
        "large_image": "ger",
        "large_text": "German Reich · Operation Postern 1.19.2",
        "small_image": "fascism",
        "small_text": "Fascist",
        "start": START,
    }


def test_unknown_country_falls_back_to_the_default_image():
    payload = buildPresence(getCountry("ZZZ"), HEADER, START)

    assert payload["large_image"] == DEFAULT_LARGE_IMAGE
    assert payload["details"] == "ZZZ — Fascist"


@pytest.mark.parametrize(
    ("difficulty", "expected"),
    [
        ("very_easy", "Civilian"),
        ("easy", "Recruit"),
        ("normal", "Regular"),
        ("hard", "Veteran"),
        ("very_hard", "Elite"),
    ],
)
def test_difficulty_uses_the_name_the_game_shows(difficulty, expected):
    """Regression: the save's internal name went straight onto the presence."""
    assert payloadFor(difficulty=difficulty)["state"].endswith(f"· {expected}")


@pytest.mark.parametrize(
    ("ideology", "expected"),
    [
        ("fascism", "Fascist"),
        ("democratic", "Democratic"),
        ("communism", "Communist"),
        ("neutrality", "Non-Aligned"),
        ("anarchism", "Anarchist"),
    ],
)
def test_ideology_uses_the_name_the_game_shows(ideology, expected):
    payload = payloadFor(ideology=ideology)

    assert payload["small_text"] == expected
    assert payload["details"].endswith(f"— {expected}")
    assert payload["small_image"] == ideology


def test_an_unknown_value_is_made_presentable_rather_than_shown_raw():
    """A HOI4 patch adding a difficulty must not put `some_new_mode` on screen."""
    payload = payloadFor(difficulty="some_new_mode", ideology="syndicalism")

    assert "Some New Mode" in payload["state"]
    assert payload["small_text"] == "Syndicalism"
    assert payload["small_image"] == UNKNOWN_IDEOLOGY_IMAGE


def test_ironman_takes_the_small_image_and_is_named_everywhere():
    payload = payloadFor(ironman=True, difficulty="very_hard")

    assert payload["state"] == "1 Jan 1936 · Elite · Ironman"
    assert payload["small_image"] == IRONMAN_IMAGE
    assert payload["small_text"] == "Fascist · Ironman"


def test_a_normal_run_says_nothing_about_ironman():
    payload = payloadFor()

    assert "Ironman" not in payload["state"]
    assert "Ironman" not in payload["small_text"]
    assert payload["small_image"] != IRONMAN_IMAGE


def test_a_save_without_a_version_does_not_leave_a_dangling_separator():
    assert payloadFor(version="")["large_text"] == "German Reich"


@pytest.mark.parametrize(
    ("sample", "difficulty"),
    [
        ("civilian-france", "Civilian"),
        ("recruit-japan", "Recruit"),
        ("regular-sov", "Regular"),
        ("usa-veteran", "Veteran"),
        ("ger-elite", "Elite"),
        ("tibet-ironman-elite", "Elite"),
    ],
)
def test_the_sample_saves_map_to_the_difficulty_their_name_claims(repoRoot, sample, difficulty):
    """The mapping came from real saves, so real saves are what pin it.

    Each file under `src/save games/` is the trimmed header of a campaign started
    on the difficulty in its name, so this fails if the table is ever edited to
    disagree with the game.
    """
    header = parseSaveHeader(readSaveHeader(repoRoot / "src" / "save games" / f"{sample}.hoi4"))
    payload = buildPresence(getCountry(header.tag), header, START)

    assert difficulty in payload["state"]
    assert ("Ironman" in payload["state"]) is ("ironman" in sample)


def test_idle_payload_has_no_country():
    payload = buildIdlePresence(START)

    assert payload == {
        "details": "Preparing for war...",
        "large_image": LOGO_IMAGE,
        "large_text": "thiaudiott/hoi4-presence on Github!",
        "start": START,
    }


def test_payloads_use_only_the_expected_pypresence_keywords():
    """A keyword pypresence does not accept raises TypeError inside the loop.

    Frozen set rather than pypresence's own signature: no lane that runs pytest
    installs pypresence, so the signature check this replaces was skipped in
    every environment and never guarded anything. This at least pins the payload
    shape, so a stray key cannot be added without a decision.
    """
    expected = {"state", "details", "large_image", "large_text", "small_image", "small_text", "start"}

    assert set(buildPresence(getCountry("GER"), HEADER, START)) == expected
    assert set(buildIdlePresence(START)) <= expected
