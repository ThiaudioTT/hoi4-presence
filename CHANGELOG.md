# Changelog

All notable changes to this project are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
The current version lives in [`version.json`](version.json).

Entries before `1.3.0` were reconstructed from the git history and are
summaries rather than a complete record.

## [Unreleased]

### Added

- A console UI for `setup.exe`, `uninstall.exe` and `checkupdate.exe`, built on
  `rich`. Each stage of an install now gets a labelled progress bar that stays on
  screen for at least 1.2 seconds, so the whole thing is watchable instead of a
  wall of `print` output that scrolled past in well under a second. Errors get a
  panel and wait for a keypress rather than a three-second `sleep`.

  `checkupdate.exe` had a console window it never wrote anything to — every
  message went to `checkupdate.log`, so a download in progress looked like a
  blank box sitting on top of the game. It now shows a real byte-count bar, and
  only when there is actually an update: the up-to-date path still writes nothing
  and exits immediately, because it runs on every single launch.

  After a successful install, `setup.exe` cycles block-art flags for the seven
  majors for about three seconds.
- A pytest suite covering the country table, save parsing, presence payloads,
  path discovery, the updater and the installer transforms.
- A `Tests` workflow running ruff and pytest on Linux and Windows. Both build
  workflows now depend on it, so a failing suite no longer ships a release.
- The presence writes a rotating `hoi4Presence.log` next to the executable and
  the updater writes `checkupdate.log` beside it. They are built without a
  console window, so until now every error message and every swallowed
  exception went nowhere.
- `AGENTS.md`, `docs/architecture.md` and this changelog.

### Removed

- `runRPC.bat`. `runRPC.exe` now starts the game, the updater and the presence
  itself instead of shelling out to a batch file that did nothing but three
  `start` calls and carry the documents path. That path moved to `runRPC.cfg`,
  a one-line UTF-8 file the installer writes into the game folder.

  This takes `cmd.exe` out of the launch chain, and with it three sharp edges:
  `shell=True`, the console-codepage read/write that corrupted any non-ASCII
  documents path, and a `.bat` stored with LF endings and no `.gitattributes`.
  The shim now starts the game *before* reading the config, so a broken install
  costs the presence rather than the Play button. `setup.exe` and
  `uninstall.exe` delete any `runRPC.bat` left over from a 1.3.x install.

### Changed

- The release lanes were renamed. `main` now publishes a `beta` prerelease
  titled "Beta release" instead of the `development` one, and the `test` lane
  moved to the `dev` branch as a `dev` prerelease titled "Testers build". Both
  carry a description saying what the build is for. The `main` lane publishes
  through the `gh` CLI now, like the other one; the archived
  `marvinpinto/action-automatic-releases` had no way to set release notes.
- Reorganised the source into a `hoi4presence` package with the entry-point
  scripts in `src/entrypoints/`. Nothing runs at import time any more; each
  executable has a `main()`. The built executable names are unchanged.
- `getCountry` no longer writes unknown tags back into the country table, which
  used to grow it for the lifetime of the process.
- Save headers are parsed by key rather than by position, so a truncated or
  binary save raises a clear `SaveParseError` instead of an `IndexError` that
  was silently discarded.
- The installer and uninstaller share their directory-discovery and settings
  transforms instead of duplicating roughly forty lines between them.
- The presence opens its Discord connection inside the poll loop instead of once
  at startup, so Discord not being up yet — or restarting mid-session — is a
  retry rather than the end of the session.
- The updater fetches the release **by tag** (`/releases/tags/v<version>`) rather
  than through `/releases/latest`, using the version it already read from
  `version.json`. This also drops a second GitHub API request per check, since
  the release payload already carries its assets.
- The installer always rewrites the documents path in `runRPC.bat` instead of
  only doing so for non-default folders.
- `runRPC.bat` derives the documents folder from `%USERPROFILE%` rather than
  `C:\Users\%USERNAME%`.
- The filenames shared by the installer, the uninstaller and the payload check
  (`runRPC.bat`, `runRPC.exe`, `hoi4Presence.exe`, `launcher-settings.json`) are
  defined once in `hoi4presence.install.steps`.
- `checkupdate.exe` starts `setup.exe -update` after it has finished with the
  console rather than before. `start_new_session` does not give the child its own
  console on Windows, so the two would have been drawing over each other.
- `setupLogging` takes `stream=False`. A `StreamHandler` binds `sys.stderr` when
  it is constructed, so one created before a progress bar starts cannot be
  intercepted by it, and its records land on the terminal raw.
- `release.formatProgress` is gone; `rich` renders the download progress now.

### Fixed

- Both build workflows could fail to replace their rolling prerelease. The step
  was `gh release delete <tag> --yes --cleanup-tag || echo "no existing release"`,
  which swallowed every failure rather than just "there was nothing to delete" —
  so a transient `HTTP 503` from the GitHub API read as success, and the
  `gh release create` that followed died with *"a release with the same tag name
  already exists"*. The delete is now retried, only a genuine absence is allowed
  through, and a build that cannot clear the old release fails loudly instead of
  publishing over it. A tag left behind by a half-completed delete is cleared
  too, since `gh release create` silently attaches to an existing tag and
  ignores `--target`, which would publish the build against an older commit.
- The build workflows now check that a `.zip` was actually produced before
  publishing, rather than letting `Get-Item *.zip` match nothing.
- `ICE` was defined twice in the country table; the second entry silently won,
  so Iceland used a wiki URL and its uploaded flag asset was never shown.
- `BEG` (Benishangul-Gumuz Nation) was showing Bangladesh's flag. No verified
  image is available, so it falls back to the default logo for now.
- The installer's required-file check was inverted: it reported unexpected extra
  files as "not found" and could not detect a genuinely missing executable.
- The updater read the whole release into memory to compute a progress
  percentage, defeating its own streaming download and crashing on an empty
  response. It also tried to unpack a missing asset instead of reporting that
  there was nothing to install.
- Running `checkupdate` from a source checkout no longer reads a stale
  `0.1.0` version stub and tries to install a "newer" release over a
  developer's working copy.
- The release workflow referenced `LICENSE.txt`; the file is `LICENSE.TXT`.
- `runRPC.bat` built the documents path from `%USERNAME%` while the installer
  decided whether to rewrite it by comparing against `%USERPROFILE%`. Where the
  profile folder name differs from the account name — a renamed account, a
  domain profile, a profile on another drive — the installer reported success
  and neither the presence nor the updater ever started, with no log to say why.
- Finishing an auto-update started `runRPC.exe`, which runs `runRPC.bat`, which
  starts `hoi4.exe` — a second copy of the game on top of the one being played.
  It now starts the presence itself.
- `taskkill` exits 128 when the target is not running, and the installer treated
  any non-zero code as fatal, so an auto-update aborted whenever the presence
  had already exited. The kill is best-effort now.
- The auto-updater passed the real `input()` to the folder-discovery loop, so a
  user whose documents or game folder was not at the default left `setup.exe`
  waiting forever on a console nobody was looking at — after it had already
  stopped the running presence. It now fails with a logged reason.
- A documents folder containing `[` or `]`, such as `D:\Games [SSD]`, was read as
  a glob character class, so no save ever matched and the presence stayed on the
  idle payload for the whole session.
- The two diagnostics that explain a stuck presence — no save matched, newest
  save too old — were logged below the log file's level, so the log users are
  asked to attach was empty in exactly that case.
- A path pasted from Explorer's "Copy as path" arrives wrapped in quotes, which
  never resolved, so the installer re-prompted forever.
- Uninstalling twice, or after the install folder had been deleted by hand,
  aborted on the folder removal and left `runRPC.bat` and `runRPC.exe` in the
  game folder.
- The installer resolved its payload from the working directory, so "Run as
  administrator" made it look in `System32`. It now looks next to `setup.exe`.
- A GitHub API error, such as a rate-limited 403, was parsed as a release and
  surfaced later as an unexplained `KeyError`.
- The downloaded release zip is deleted from `%TEMP%` after it is unpacked.
- The installer no longer tells the user to delete the folder holding the only
  copy of `uninstall.exe`.

### Removed

- `tests/` no longer holds the 2022 scratch scripts (`openfile.py`,
  `openfileNOBinary.py`, `path.py`, `time.py`, `echoDocument.bat`); it is a real
  test suite now. `tests/demo.PNG` moved to `docs/demo.PNG`.
- The stale `src/checkupdate/version.json` development stub.
- `tools/getVanillaCountries.py`, the one-shot wiki scraper whose output was
  merged into `countries.py` by hand years ago. It imported `requests`, which
  `requirements-dev.txt` does not install, so it could not run at all under the
  documented development setup, and its wiki selectors were positional. The
  `beautifulsoup4` development dependency went with it.
- The `pypresence` signature check in `tests/test_presence.py`, which was skipped
  in every environment that runs the suite and therefore never guarded anything.
  The payload key set is asserted directly instead.

### Known issues

- A stable release tag still has to be exactly `v<version>`: the asset name the
  updater looks for is derived from it. The updater no longer mistakes the
  rolling `development` and `test` prereleases for an update, because it asks
  for the tag matching `version.json` rather than for `/releases/latest`.
- `runRPC.bat` is an indirection the launcher shim could absorb, but it is still
  referenced by the installer, the uninstaller and `build.spec`.
- 146 of the 172 URL-based country flags point at `hoi4.paradoxwikis.com`, which
  now answers every image request with an anti-bot challenge page rather than the
  PNG. Those countries almost certainly render without a flag in Discord. The 25
  `i.imgur.com` links and the 92 Discord developer-portal asset keys are
  unaffected. Re-hosting them is a data migration and belongs in its own change.

## [1.3.0]

### Added

- `runRPC.exe`, a launcher shim, because the Paradox launcher cannot spawn a
  `.bat` directly — this fixes the game not starting through the launcher.
- A `development` build workflow, and a `test` release lane (renamed from
  `develop`).
- Threading in `tools/getVanillaCountries.py` to speed up scraping.

### Fixed

- The presence not running after setup.

## [1.2.3]

### Added

- Country flag images as local assets under `assets/`.

### Fixed

- Spain not appearing.
- Flag scraping in `tools/getVanillaCountries.py`.

## [1.2.2]

### Changed

- New default details text in the presence.

### Fixed

- The default large image not appearing.

## [1.2.1]

### Fixed

- `setup`/`uninstall` now read and write files as UTF-8.

### Changed

- Documentation moved and expanded; badges added to the readme.

## [1.2.0]

### Added

- The `auto-update` setting.

### Fixed

- Running instances are closed before installing.
- `checkupdate` passes a working directory so the installer knows where it is.

## [1.1.0]

### Added

- An uninstaller.

### Fixed

- `psutil` added to the requirements.

## [1.0.0]

First stable release.

[Unreleased]: https://github.com/ThiaudioTT/hoi4-presence/compare/v1.3.0...HEAD
[1.3.0]: https://github.com/ThiaudioTT/hoi4-presence/compare/v1.2.3...v1.3.0
[1.2.3]: https://github.com/ThiaudioTT/hoi4-presence/compare/v1.2.2...v1.2.3
[1.2.2]: https://github.com/ThiaudioTT/hoi4-presence/compare/v1.2.1...v1.2.2
[1.2.1]: https://github.com/ThiaudioTT/hoi4-presence/compare/v1.2.0...v1.2.1
[1.2.0]: https://github.com/ThiaudioTT/hoi4-presence/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/ThiaudioTT/hoi4-presence/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/ThiaudioTT/hoi4-presence/releases/tag/v1.0.0
