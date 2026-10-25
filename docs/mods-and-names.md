# Mods, country names and the settings file

What the presence shows on a modded run, where each piece comes from, and how
a player tunes it. For the runtime chain and the polling loop, see
[architecture.md](architecture.md).

## What a modded card looks like

```
Hearts of Iron IV
Deutsches Reich — Fascist
9 Feb 1936 · Regular
```

Hovering the flag shows `The Road to 56 + Road to 56 : Expanded + 8 mods`.

| On the card         | Vanilla run                          | Modded run                                  |
| ------------------- | ------------------------------------ | ------------------------------------------- |
| first line          | `German Reich — Fascist`             | the country **as the game names it**        |
| second line         | `15 Jan 1936 · Elite · Ironman`      | unchanged                                   |
| hovering the flag   | country and game patch               | the mod line                                |

The mod line sits in the flag's hover text, as the maintainer asked in #63; a
setting to choose where it goes could come later, from the installer.

A vanilla run (no mod enabled in the launcher) produces exactly the payload it
did before these changes; the existing payload tests in `tests/test_presence.py`
pass unchanged.

## The mod line

### Where the mods come from

Just before it starts the game, the Paradox launcher writes the enabled playset
to `dlc_load.json` in the HOI4 documents folder:

```json
{"enabled_mods": ["mod/ugc_820260968.mod", "mod/ugc_3506850939.mod"], "disabled_dlcs": []}
```

Each entry is a `.mod` descriptor (`hoi4presence.mods.readDescriptor`). From
it the presence takes `name`, `path` (or `archive`), every `replace_path` and
the `dependencies` block. Relative paths are relative to the documents folder;
`C:/...` paths are kept as they are. A missing or malformed file never stops
the presence: it simply shows no mod line. The idle card ("Preparing for
war...") is unchanged.

### How the line is built

A real playset is one large mod surrounded by small ones (icons, music, map
modes, compatibility patches). Naming every mod overflows Discord's 128
characters long before the interesting one is reached, so by default
(`"mod_line": "auto"`) `hoi4presence.mods.modLabel` does this:

1. **Overhauls are named.** An overhaul is a mod whose `replace_path` throws
   away the game's own copy of the world: any path starting with
   `history/countries`, `history/states`, `common/national_focus`,
   `common/countries` or `events` (`mods.WORLD_PATHS`). The Fire Rises, The
   Road to 56, Kaiserreich, The Great War Redux, Old World Blues and Darkest
   Hour all qualify; a mod that only replaces `gfx/loadingscreens` does not.
2. **Submods of an overhaul are named after it.** A submod is a mod whose
   `dependencies` name an overhaul that is enabled: Road to 56 : Expanded on
   The Road to 56, Yugoslavia Reborn on The Fire Rises. A compatibility patch
   that lists ten overhauls is only a submod if one of them is in the playset.
3. **Pinned mods** (`pinned_mods`) are named next.
4. **Everything else is counted**: `+ 8 mods`, or `+ 1 mod`.
5. With no overhaul at all, the line starts with `Vanilla`: `Vanilla + 5 mods`.

Overhauls come first whatever the load order, then submods, then pinned mods;
each group keeps load order. `"mod_line": "all"` names every mod instead. Whatever the mode, `presence.fitField` cuts
any text over 128 characters with `…` rather than letting Discord reject the
whole update.

## The country name

The save header only holds the tag (`player="GER"`). The name shown is the
first of these that gives one (`hoi4presence.session.resolveCountry`):

1. **The player's settings file**, `countries.<TAG>.name`.
2. **`continue_game.json`**, which the game writes in the documents folder on
   every save for the main menu's *Continue* button:

   ```json
   {"title": "Deutsches Reich 1936.2.9.9", "filename": "GER_1936_02_09_09.hoi4", ...}
   ```

   The title is the name exactly as the game displays it, with mods, cosmetic
   tags and the interface language already applied. The trailing date is cut
   off. It is only used when `filename` is the save being shown, since after
   loading an older save the file still describes the last one written.
3. **The enabled mods' localisation** (`hoi4presence.localisation`). For the
   tag, the presence scans every mod's `localisation/**/*.yml` for `TAG` and
   `TAG_<lowercase suffix>` keys, then picks `TAG_<ideology>` before `TAG`, in
   the game's language (`language=` in `settings.txt`) before `l_english`.
   Names built from scripted localisation (`[GER.GetName]`) or variables are
   skipped. Precedence follows the game:
   - files under a `replace` folder override every other file, whichever mod
     they come from. This is how Native Country Names' `Deutsches Reich` beats
     The Road to 56's `German Reich` although The Road to 56 loads later;
   - among files of the same kind, a mod later in the load order overrides an
     earlier one.

   The scan runs once per tag and playset (`CountryNames` caches it); on a
   large overhaul it reads a few thousand matching lines.
4. **The built-in table** in `countries.py`, as before.

The flag still comes from the table, by tag, unless the settings file sets one.

### Known limits

- A cosmetic tag (a formed Yugoslavia that is still `SER` underneath) is only
  named correctly through `continue_game.json`; localisation alone sees `SER`.
  Whether autosaves rewrite `continue_game.json` was not checked: when it
  describes another file, the localisation is used, and the player can still
  set the name in the settings file.
- The precedence between two ordinary (non-`replace`) files defining the same
  key was not checked against the game's source; it follows load order, which
  matched every case that was tried.

## What follows "Playing" in the member list

Discord shows the application name ("Hearts of Iron IV") after *Playing* next
to a member's name. `status_text` set to `"country"` replaces it with the
country line. It sets the activity's `status_display_type`; the profile card's
title stays the application name. The default, `"game"`, sends nothing and
keeps Discord's own behaviour.

## The settings file

`hoi4Presence-settings.json`, in the HOI4 documents folder next to
`settings.txt`. It lives there rather than in `hoi4Presence/` because
`setup.exe` deletes and recreates that folder on every reinstall. The presence
writes a template with `_help` entries the first time it runs, never overwrites
an existing file, and rereads it on every poll, so an edit shows on Discord
within a minute without restarting the game. Invalid JSON is logged and the
defaults are used.

| Key           | Default  | Meaning                                                                 |
| ------------- | -------- | ----------------------------------------------------------------------- |
| `show_mods`   | `true`   | `false` removes the mod line; the hover text goes back to the patch     |
| `mod_line`    | `"auto"` | `"auto"` as described above, or `"all"` to name every mod               |
| `pinned_mods` | `[]`     | mods to name in `"auto"` mode instead of counting them                  |
| `hidden_mods` | `[]`     | mods neither named nor counted                                          |
| `mod_names`   | `{}`     | `{"Full launcher name": "Short name"}`                                  |
| `status_text` | `"game"` | `"game"` or `"country"`, see above                                      |
| `countries`   | `{}`     | `{"TAG": {"name": "...", "flag": "https://...png"}}`, both optional     |

Mod names are matched without regard to case or surrounding spaces, since they
are typed by hand. A flag that is not an `https://` link is ignored, because
Discord would show no image at all.

## Flags

147 of the 172 URL flags in `countries.py` pointed at `hoi4.paradoxwikis.com`,
and all of them but Serbia's now return a 3 KB anti-bot page with HTTP 200, so
Discord, which fetches the image server side, showed no flag. They were
replaced by Wikimedia Commons thumbnails of the real-world flag:

- 138 entries, Serbia included, now use
  `https://upload.wikimedia.org/wikipedia/commons/thumb/.../330px-<file>.png`.
  The width is 330px because Wikimedia only serves its standard widths (320px
  returns HTTP 400).
- The files were looked up through the Commons API, and each thumbnail was
  fetched with Discord's user agent and checked to be a PNG before being kept,
  except NEN and RIF, whose checks Wikimedia rate-limited.
- Nine countries with no real-world flag (CSA, AOI, GBA, HRZ, KHI, GUM, NIR,
  QEM, VLA) now use the default logo, like BEG already did. Their in-game
  flags would need to be uploaded to the Discord developer portal.

## Code map

| Module                         | Role                                                                        |
| ------------------------------ | --------------------------------------------------------------------------- |
| `hoi4presence/mods.py`         | read `dlc_load.json` and the descriptors; build the mod line                |
| `hoi4presence/localisation.py` | scan mod localisation for a tag; game language from `settings.txt`          |
| `hoi4presence/session.py`      | gather everything above once per poll; `continue_game.json`; pick the name |
| `hoi4presence/userconfig.py`   | the settings file: template, parsing, defaults                              |
| `hoi4presence/presence.py`     | `fitField`, the mod line in the hover text, `status_display_type`           |
| `hoi4presence/runner.py`       | reads the session each poll; sends an update only when the payload changes |

None of the new modules imports `pypresence` or `psutil`, so they are tested on
Linux like the rest of the library. `runner.toPypresence` turns the plain
`status_display_type` number into pypresence's `StatusDisplayType` at the last
moment. The entry point passes the documents folder (the parent of
`hoi4Presence/`) to `runner.run`; from a source checkout that is `src/`, which
holds none of these files, so the presence runs as before.
