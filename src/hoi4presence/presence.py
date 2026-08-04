"""Building the payloads sent to Discord.

Kept free of :mod:`pypresence` on purpose: the payload is the part worth
testing, and keeping the dependency out means the suite runs anywhere.
"""

from __future__ import annotations

from hoi4presence.countries import Country
from hoi4presence.saves import SaveHeader

# Discord developer-portal asset keys for the app's own artwork.
LOGO_IMAGE = "hoi4-logo"

IDLE_DETAILS = "Preparing for war..."
LOGO_TEXT = "thiaudiott/hoi4-presence on Github!"


def buildIdlePresence(start: float) -> dict[str, object]:
    """Payload shown after connecting, before any save has been read."""
    return {
        "details": IDLE_DETAILS,
        "large_image": LOGO_IMAGE,
        "large_text": LOGO_TEXT,
        "start": start,
    }


def buildPresence(country: Country, header: SaveHeader, start: float) -> dict[str, object]:
    """Payload describing the current run, ready to splat into ``RPC.update``."""
    return {
        "state": f"Year: {header.year}",
        "details": f"Playing as {country.name}",
        "large_image": country.flag,
        "large_text": f"Ideology: {header.ideology}",
        "small_image": LOGO_IMAGE,
        "small_text": f"In {header.difficulty} mode",
        "start": start,
    }
