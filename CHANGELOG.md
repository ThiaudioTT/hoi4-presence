# Changelog

All notable changes to this project are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
The current version lives in [`version.json`](version.json).

Entries before `1.3.0` were reconstructed from the git history and are
summaries rather than a complete record.

## [Unreleased]

### Added

- A pytest suite covering the country table, save parsing, presence payloads,
  path discovery, the updater and the installer transforms.
- A `Tests` workflow running ruff and pytest on Linux and Windows. Both build
  workflows now depend on it, so a failing suite no longer ships a release.
- The presence and the updater write a rotating `hoi4Presence.log` next to the
  executable. They are built without a console window, so until now every error
  message and every swallowed exception went nowhere.
- `AGENTS.md`, `docs/architecture.md` and this changelog.

### Changed

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

### Fixed

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

### Removed

- `tests/` no longer holds the 2022 scratch scripts (`openfile.py`,
  `openfileNOBinary.py`, `path.py`, `time.py`, `echoDocument.bat`); it is a real
  test suite now. `tests/demo.PNG` moved to `docs/demo.PNG`.
- The stale `src/checkupdate/version.json` development stub.

### Known issues

- The auto-updater looks for a release asset named
  `hoi4-presence-{tag_name}.zip` while the build produces
  `hoi4-presence-v{version}.zip`. These only agree when a release tag is exactly
  `v<version>`; both CI lanes publish to the rolling tags `development` and
  `test`, so a client whose `/releases/latest` resolves to one of those finds no
  asset and does nothing.
- `runRPC.bat` is an indirection the launcher shim could absorb, but it is still
  referenced by the installer, the uninstaller and `build.spec`.

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
