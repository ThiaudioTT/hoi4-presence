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
       ├─ hoi4.exe -gdpr-compliant
       ├─ checkupdate.exe   (src/entrypoints/checkupdate.py)
       └─ hoi4Presence.exe  (src/entrypoints/hoi4RPC.py)
```

`runRPC.exe` exists because the launcher prepends its own arguments (session
token, account id), so the shim re-launches the game with the argument order we
control.

It finds the other two executables by reading `runRPC.cfg`, a one-line UTF-8 file
the installer drops beside it holding the documents path it resolved — the one
thing the shim cannot work out for itself, since the documents folder is not
always where `%USERPROFILE%` says it is.

The game is started **first and unconditionally**, outside the `try`. `runRPC` is
built with `console=False`, so a failure in here is invisible; a missing or
corrupt `runRPC.cfg` has to cost the presence, never the Play button.

## The polling loop

`hoi4presence.runner.run` does this every 30 seconds:

1. glob `../save games/*.hoi4`, relative to the executable — installed that
   resolves to the real HOI4 save folder, and from a source checkout to
   `src/save games/`;
2. take the most recently modified one;
3. skip it unless it was modified in the last **120 seconds**, so a save left
   over from a previous session is not reported as current;
4. read the first **20 lines**, then close the handle immediately — HOI4 needs
   write access to the file it is autosaving into. Only five of those lines are
   used; the wider window keeps a HOI4 patch that inserts a header field from
   pushing `difficulty` out of range;
5. parse those lines into a `SaveHeader`, map the tag to a `Country`, and push
   the payload to Discord;
6. exit once `hoi4.exe` is no longer in the process list.

The Discord connection is opened *inside* the loop, not once up front. Discord
is started by the user rather than by us, so it may not be up when the game
launches, and it restarts itself often enough that a session-long connection
cannot be assumed. A failed update drops the connection so the next poll
reconnects; a failed save read does not, because reconnecting would not help.

Those constants live at the top of `hoi4presence.saves` and
`hoi4presence.runner`.

## What the installer changes on disk

`setup.exe` touches four things, and `uninstall.exe` reverses each one:

| Location | Change |
| --- | --- |
| `Documents\...\Hearts of Iron IV\hoi4Presence\` | the payload is copied here |
| `Documents\...\Hearts of Iron IV\settings.txt` | `save_as_binary=yes` → `no` |
| `<game folder>\runRPC.exe` | copied in, plus a generated `runRPC.cfg` |
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

## Updating

`checkupdate.exe` runs alongside the game and writes its own `checkupdate.log`
— it and `hoi4Presence.exe` start together, and a `RotatingFileHandler` shared
between two processes breaks on rollover.

It compares the local `version.json` with the copy on `main`, and if
`auto-update` is on and the local one is older it fetches the release tagged
`v<that version>`, unpacks it to `%TEMP%` and hands over to `setup.exe -update`,
which reinstalls without prompting and restarts the presence.

The release is fetched **by tag**, not through `/releases/latest`. Those are two
different things: the version that triggers an update comes from `version.json`
on `main`, while `/releases/latest` can resolve to a rolling prerelease such as
`beta`, or to the previous stable release while the new tag has not been
pushed yet — whose asset would reinstall the version the user already has, on
every launch. Fetching by tag also means the tag has to be exactly `v<version>`,
which is what `build.spec` names the zip.

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
    version.json
```

`hoi4Presence` and `runRPC` are built with `console=False`, which is why
everything they report goes to `hoi4Presence.log` rather than to stdout.
