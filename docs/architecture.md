# Architecture

How the pieces fit together, for people changing the code. For what the project
*does*, see the [readme](../readme.md).

## The idea

HOI4 has no API and no mod hook that can reach Discord. What it does have is an
autosave written to disk every in-game month. So the presence polls that file.

The catch is that HOI4 saves in a binary format by default, which is why the
installer flips `save_as_binary=no` — with plaintext saves, the first few lines
are all the presence needs:

```
HOI4txt
player="GER"
ideology=fascism
date="1936.1.1.12"
difficulty="normal"
```

## Runtime chain

The installer points the Paradox launcher at a shim rather than the game, so
starting the game normally also starts the presence:

```
Paradox launcher
  └─ runRPC.exe          (src/entrypoints/launcher.py)
       └─ runRPC.bat     (src/runRPC.bat)
            ├─ hoi4.exe -gdpr-compliant
            ├─ checkupdate.exe   (src/entrypoints/checkupdate.py)
            └─ hoi4Presence.exe  (src/entrypoints/hoi4RPC.py)
```

`runRPC.exe` exists because the launcher spawns its target without a shell and
therefore cannot run a `.bat` directly. It also prepends its own arguments
(session token, account id), so the shim re-launches with the argument order we
control.

## The polling loop

`hoi4presence.runner.run` does this every 30 seconds:

1. glob `../save games/*.hoi4`, relative to the executable — installed that
   resolves to the real HOI4 save folder, and from a source checkout to
   `src/save games/`;
2. take the most recently modified one;
3. skip it unless it was modified in the last **120 seconds**, so a save left
   over from a previous session is not reported as current;
4. read the first **5 lines**, then close the handle immediately — HOI4 needs
   write access to the file it is autosaving into;
5. parse those lines into a `SaveHeader`, map the tag to a `Country`, and push
   the payload to Discord;
6. exit once `hoi4.exe` is no longer in the process list.

Those constants live at the top of `hoi4presence.saves` and
`hoi4presence.runner`.

## What the installer changes on disk

`setup.exe` touches four things, and `uninstall.exe` reverses each one:

| Location | Change |
| --- | --- |
| `Documents\...\Hearts of Iron IV\hoi4Presence\` | the payload is copied here |
| `Documents\...\Hearts of Iron IV\settings.txt` | `save_as_binary=yes` → `no` |
| `<game folder>\runRPC.exe`, `runRPC.bat` | copied in |
| `<game folder>\launcher-settings.json` | `exePath` → `./runRPC.exe`, `exeArgs` → `[]` |

Both find those folders by looking for a marker file (`settings.txt` and
`hoi4.exe` respectively) and asking the user if it is not where it should be.
The transforms themselves are pure functions in `hoi4presence.install.steps`, so
they are tested without a HOI4 install.

## Country flags

`hoi4presence.countries` maps a three-letter tag to a display name and an image,
and the image comes in two flavours:

- **a short key** such as `"ger"` names an asset uploaded to the Discord
  developer portal. Every one is mirrored as a PNG under
  `assets/initialCountries/` so the set is reviewable in the repo. Nothing reads
  those files at runtime — the mirror exists for humans, and
  `tests/test_countries_data.py` keeps the two sides in sync.
- **a full URL**, mostly to the HOI4 wiki, for releasable countries that the
  portal does not host.

`tools/getVanillaCountries.py` scraped the initial table; its output was merged
into `countries.py` by hand. It is a one-shot dev tool, not part of the build.

## Updating

`checkupdate.exe` runs alongside the game. It compares the local `version.json`
with the copy on `main`, and if `auto-update` is on and the local one is older it
downloads the release asset, unpacks it to `%TEMP%` and hands over to
`setup.exe -update`, which reinstalls without prompting and restarts the
presence.

The asset name is derived from the release tag, so a stable release tag has to be
exactly `v<version>` to match what `build.spec` produces. See the known-issues
note in [AGENTS.md](../AGENTS.md).

## Building

`build.spec` builds five executables from the scripts in `src/entrypoints/`, then
assembles them into `hoi4-presence-v<version>.zip`:

```
setup.exe
uninstall.exe
discordRPC/dist/
    hoi4Presence.exe
    checkupdate.exe
    runRPC.exe
    runRPC.bat
    version.json
```

`hoi4Presence` and `runRPC` are built with `console=False`, which is why
everything they report goes to `hoi4Presence.log` rather than to stdout.
