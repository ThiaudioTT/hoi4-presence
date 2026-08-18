"""Building the payloads sent to Discord.

Kept free of :mod:`pypresence` on purpose: the payload is the part worth
testing, and keeping the dependency out means the suite runs anywhere.

The save stores HOI4's internal names -- ``very_hard``, ``neutrality`` -- which
are not what the game shows the player. Everything user-facing goes through
:func:`displayName` so the presence says "Elite" and "Non-Aligned" like the
game does.
"""

from __future__ import annotations

from hoi4presence.countries import Country
from hoi4presence.saves import SaveHeader

# Discord developer-portal asset keys for the app's own artwork.
LOGO_IMAGE = "hoi4-logo"
IRONMAN_IMAGE = "ironman"
# The game's own "unknown ideology" icon, shown for an ideology added by a mod.
UNKNOWN_IDEOLOGY_IMAGE = "unknown-ideology"

IDLE_DETAILS = "Preparing for war..."
LOGO_TEXT = "thiaudiott/hoi4-presence on Github!"

SEPARATOR = " · "

# Save value -> the difficulty name the game's own menu uses.
DIFFICULTY_NAMES = {
    "very_easy": "Civilian",
    "easy": "Recruit",
    "normal": "Regular",
    "hard": "Veteran",
    "very_hard": "Elite",
}

# Save value -> the ideology name the game uses. Each of these keys doubles as
# the portal asset key for its badge, mirrored in assets/ideologies/.
IDEOLOGY_NAMES = {
    "fascism": "Fascist",
    "democratic": "Democratic",
    "communism": "Communist",
    "neutrality": "Non-Aligned",
    # Not in the base game; some mods use it, and the wiki has the icon.
    "anarchism": "Anarchist",
}


def displayName(value: str, names: dict[str, str]) -> str:
    """Map a save value to its in-game name, or make the raw value presentable.

    The fallback matters: a HOI4 patch adding an ideology would otherwise put a
    bare ``some_new_thing`` on the presence.
    """
    return names.get(value, value.replace("_", " ").title())


def ideologyImage(ideology: str) -> str:
    """Portal asset key for an ideology, or the game's "unknown ideology" icon."""
    return ideology if ideology in IDEOLOGY_NAMES else UNKNOWN_IDEOLOGY_IMAGE


def buildIdlePresence(start: float) -> dict[str, object]:
    """Payload shown after connecting, before any save has been read."""
    return {
        "details": IDLE_DETAILS,
        "large_image": LOGO_IMAGE,
        "large_text": LOGO_TEXT,
        "start": start,
    }


def buildPresence(country: Country, header: SaveHeader, start: float) -> dict[str, object]:
    """Payload describing the current run, ready to splat into ``RPC.update``.

    Ironman takes the small image when it applies: it is the rarer, more
    interesting fact about a run, and the ideology it displaces is still named
    in the hover text right beside it.
    """
    ideology = displayName(header.ideology, IDEOLOGY_NAMES)
    difficulty = displayName(header.difficulty, DIFFICULTY_NAMES)
    ironman = ["Ironman"] if header.ironman else []

    return {
        "state": SEPARATOR.join([header.dateLabel, difficulty, *ironman]),
        "details": f"{country.name} — {ideology}",
        "large_image": country.flag,
        # versionLabel is empty for a save old enough to predate the field.
        "large_text": SEPARATOR.join(filter(None, [country.name, header.versionLabel])),
        "small_image": IRONMAN_IMAGE if header.ironman else ideologyImage(header.ideology),
        "small_text": SEPARATOR.join([ideology, *ironman]),
        "start": start,
    }
