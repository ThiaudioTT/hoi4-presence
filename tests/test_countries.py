"""Behaviour of the tag -> country lookup."""

from __future__ import annotations

import pytest

from hoi4presence.countries import DEFAULT_LARGE_IMAGE, Country, countries, getCountry


def test_known_tag_returns_name_and_flag():
    assert getCountry("GER") == Country("German Reich", "ger")


def test_lowercase_tag_is_normalised():
    assert getCountry("ger") == getCountry("GER")


def test_unknown_tag_uses_the_tag_as_its_name_and_the_default_flag():
    assert getCountry("ZZZ") == Country("ZZZ", DEFAULT_LARGE_IMAGE)


def test_unknown_tag_does_not_mutate_the_table():
    """Regression: lookups used to write unknown tags back into the dict."""
    before = dict(countries)

    getCountry("ZZZ")

    assert "ZZZ" not in countries
    assert countries == before


def test_entry_without_a_flag_falls_back_to_the_default(monkeypatch):
    monkeypatch.setitem(countries, "TST", ("Testland", ""))

    assert getCountry("TST") == Country("Testland", DEFAULT_LARGE_IMAGE)
    # The fallback must not be written back into the table either.
    assert countries["TST"] == ("Testland", "")


@pytest.mark.parametrize("value", ["", None])
def test_empty_code_raises(value):
    with pytest.raises(ValueError):
        getCountry(value)


def test_civil_war_tag_survives_uppercasing():
    assert getCountry("D##").name == "Civil War Country"


def test_iceland_uses_its_uploaded_asset():
    """Regression: a duplicate "ICE" key shadowed this with a wiki URL."""
    assert getCountry("ICE") == Country("Iceland", "ice")


def test_str_is_name_then_flag():
    assert str(getCountry("GER")) == "German Reich, ger"
