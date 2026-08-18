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
version="Operation Postern v1.19.2.0.a729 (d245)"
ironman="Ironman Finland 1.hoi4"
```

`ironman` appears only in ironman saves — its presence *is* the flag — and
`version` is missing from old enough saves, so neither is required to parse.
`difficulty` holds HOI4's internal name (`very_hard`), not the one the game's own
menu shows (`Elite`); `presence.py` owns that translation.

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
   write access to the file it is autosaving into. Only seven of those lines are
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

The flag is the presence's *large* image. The small badge on its corner is the
ideology — `fascism`, `democratic`, `communism`, `neutrality` and the mod-only
`anarchism`, each name doubling as its portal asset key — replaced by `ironman`
on an ironman run, since that is the rarer fact and the ideology is still named
in the hover text. All of them are mirrored under `assets/ideologies/`, and an
ideology with no badge of its own gets the game's `unknown-ideology` icon, so one
added by a patch or a mod cannot break the payload.

## Updating

`checkupdate.exe` runs alongside the game and writes its own `checkupdate.log`
— it and `hoi4Presence.exe` start together, and a `RotatingFileHandler` shared
between two processes breaks on rollover. It logs to that file *only*: it has a
console, but that belongs to the wizard described below, and a `StreamHandler`
would print over the progress bar rather than through it.

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

## The console UI

`setup.exe`, `uninstall.exe` and `checkupdate.exe` are the three executables
built with a console, so for them the terminal *is* the interface. All three
drive `hoi4presence.ui.Wizard`, which gives each stage a progress bar and holds
it on screen for at least `MIN_STEP_SECONDS` — the real work is a JSON edit and
four file copies, which used to finish faster than anyone could read.

`Wizard.step()` yields an `onProgress(done, total)` callback. Ignore it and the
bar pulses for however long the work takes, then fills over the remainder of the
minimum; call it, as `checkupdate` does with `downloadUpdate`, and the bar tracks
real bytes instead. Either way the step leaves a permanent `✓ … DONE` line, or
`✗ … FAILED` if it raised. `Wizard.ask`/`Wizard.warn` are the prompt/log pair
`paths.findDirContaining` takes, which is how the retry loop for a non-default
install folder ends up inside the display.

`setup.exe` and `uninstall.exe` both open with `Wizard.confirm()`, so nothing is
touched until the user agrees; declining exits 0 having changed nothing.
`setup.exe` closes with `finish(flags=True)`, which cycles the majors' flags
under the success panel until Enter. The read runs on its own thread, because
rich cannot animate and block on `input()` at the same time — the animation
waits on the same event the reader sets, so Enter ends it at once instead of
after the current flag times out.

`interactive` is the one switch that matters. `setup.exe -update` runs behind the
game the user is already playing, on a console nobody is looking at, so an
auto-update passes `interactive=False`: no keypress pauses, no pacing, and
`ask()` raises rather than blocking. That last one is a fix, not a nicety — the
updater has already stopped the running presence by the time it looks for a
folder, so a user whose install is not at the default used to leave `setup.exe`
waiting forever.

Two ordering rules the code comments repeat, because breaking either is
invisible until it is on a user's screen:

- rich allows one live display at a time, so `finish(flags=True)` stops the
  progress bar before starting its own.
- `checkupdate` spawns `setup.exe -update` **after** leaving its `with` block.
  `start_new_session` does not give the child a new console on Windows, so both
  processes would otherwise be drawing on the same screen buffer.

The two windowed executables must never import this module. They are built
`console=False`, so `sys.stdout` is `None` and rich renders into a void;
`launcher.py` is stdlib-only besides. `tests/test_packaging.py` enforces it.

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
