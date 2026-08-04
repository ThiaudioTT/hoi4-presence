"""The payloads handed to Discord."""

from __future__ import annotations

from hoi4presence.countries import DEFAULT_LARGE_IMAGE, getCountry
from hoi4presence.presence import LOGO_IMAGE, buildIdlePresence, buildPresence
from hoi4presence.saves import SaveHeader

HEADER = SaveHeader(tag="GER", ideology="fascism", date="1936.1.1.12", difficulty="normal")
START = 1_700_000_000.0


def test_payload_for_a_known_country():
    assert buildPresence(getCountry("GER"), HEADER, START) == {
        "state": "Year: 1936",
        "details": "Playing as German Reich",
        "large_image": "ger",
        "large_text": "Ideology: fascism",
        "small_image": LOGO_IMAGE,
        "small_text": "In normal mode",
        "start": START,
    }


def test_unknown_country_falls_back_to_the_default_image():
    payload = buildPresence(getCountry("ZZZ"), HEADER, START)

    assert payload["large_image"] == DEFAULT_LARGE_IMAGE
    assert payload["details"] == "Playing as ZZZ"


def test_idle_payload_has_no_country():
    payload = buildIdlePresence(START)

    assert payload == {
        "details": "Preparing for war...",
        "large_image": LOGO_IMAGE,
        "large_text": "thiaudiott/hoi4-presence on Github!",
        "start": START,
    }


def test_payload_keys_are_accepted_by_pypresence():
    """Guards against pypresence renaming an update() keyword under us."""
    import inspect

    pypresence = __import__("importlib").util.find_spec("pypresence")
    if pypresence is None:
        import pytest

        pytest.skip("pypresence is not installed")

    from pypresence import Presence

    accepted = set(inspect.signature(Presence.update).parameters)
    used = set(buildPresence(getCountry("GER"), HEADER, START)) | set(buildIdlePresence(START))

    assert used <= accepted, f"payload keys pypresence does not accept: {sorted(used - accepted)}"
