"""Integrity of the country table itself.

These read countries.py as source rather than importing it, so they can see
mistakes that Python resolves silently -- a duplicate key being the main one.
"""

from __future__ import annotations

import re

from hoi4presence.countries import DEFAULT_LARGE_IMAGE

# Tags that deliberately reuse another country's flag, with the reason.
ALLOWED_SHARED_FLAGS = {
    "BAS": "British Antilles intentionally uses the UK flag",
    "USB": "Unaligned States of America intentionally uses the US flag",
}

# Tags that deliberately share a display name.
ALLOWED_SHARED_NAMES = {"France": {"FRA", "VIC"}}

# Flags that are neither an uploaded asset key nor a normal image URL.
ALLOWED_NON_IMAGE_URLS = {
    "KHA": "only image found for Khakassia is a .gif",
}


def isUrl(flag: str) -> bool:
    return flag.startswith("http")


def test_no_duplicate_tags(countriesSource):
    """Regression: "ICE" was defined twice and the second entry silently won."""
    tags = [tag for tag, _, _ in countriesSource]
    duplicates = sorted({tag for tag in tags if tags.count(tag) > 1})

    assert not duplicates, f"duplicate country tags: {duplicates}"


def test_tags_look_like_country_tags(countriesSource):
    bad = [tag for tag, _, _ in countriesSource if not re.fullmatch(r"[A-Z0-9#]{3}", tag)]

    assert not bad, f"tags that are not three uppercase characters: {bad}"


def test_no_entry_is_missing_a_flag(countriesSource):
    missing = [tag for tag, _, flag in countriesSource if not flag]

    assert not missing, f"entries with an empty flag: {missing}"


def test_every_asset_key_has_a_png(countriesSource, assetKeys):
    referenced = {flag.lower() for _, _, flag in countriesSource if not isUrl(flag) and flag != "DEFAULT_LARGE_IMAGE"}
    missing = sorted(referenced - assetKeys)

    assert not missing, f"flag keys with no PNG under assets/: {missing}"


def test_every_png_is_referenced(countriesSource, assetKeys):
    """Regression: the shadowed "ICE" entry orphaned assets/initialCountries/ICE.png."""
    referenced = {flag.lower() for _, _, flag in countriesSource if not isUrl(flag)}
    orphaned = sorted(assetKeys - referenced)

    assert not orphaned, f"PNGs under assets/ that no country references: {orphaned}"


def test_asset_keys_are_the_lowercased_tag(countriesSource):
    mismatched = [
        (tag, flag)
        for tag, _, flag in countriesSource
        if not isUrl(flag) and flag != "DEFAULT_LARGE_IMAGE" and flag != tag.lower()
    ]

    assert not mismatched, f"asset keys that are not the lowercased tag: {mismatched}"


def test_no_two_countries_share_a_flag(countriesSource):
    """Regression: BEG was pointing at Bangladesh's flag."""
    seen: dict[str, str] = {}
    collisions = []

    for tag, _, flag in countriesSource:
        if flag == "DEFAULT_LARGE_IMAGE" or flag == DEFAULT_LARGE_IMAGE or tag in ALLOWED_SHARED_FLAGS:
            continue
        if flag in seen:
            collisions.append(f"{tag} reuses the flag of {seen[flag]}: {flag}")
        seen[flag] = tag

    assert not collisions, "\n".join(collisions)


def test_no_two_countries_share_a_name(countriesSource):
    seen: dict[str, str] = {}
    collisions = []

    for tag, name, _ in countriesSource:
        if tag in ALLOWED_SHARED_NAMES.get(name, set()):
            continue
        if name in seen:
            collisions.append(f"{tag} reuses the name of {seen[name]}: {name!r}")
        seen[name] = tag

    assert not collisions, "\n".join(collisions)


def test_flag_urls_are_https_images(countriesSource):
    bad = [
        (tag, flag)
        for tag, _, flag in countriesSource
        if isUrl(flag) and tag not in ALLOWED_NON_IMAGE_URLS and not re.fullmatch(r"https://\S+\.(png|jpe?g)", flag)
    ]

    assert not bad, f"flag URLs that are not https image links: {bad}"
