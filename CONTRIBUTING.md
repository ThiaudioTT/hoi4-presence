# Contributing

Thank you so much to consider contributing to this project!

When contributing to this repository, please first discuss the change you wish to make via issue or any other method before making a change.

I separated good first issues with the label [good first issue](https://github.com/ThiaudioTT/hoi4-presence/labels/good%20first%20issue) to help you to start contributing to this project. If you want to contribute with something else, please open an issue to discuss it or search for an issue that is already open in [Issues](https://github.com/ThiaudioTT/hoi4-presence/issues).

## Getting Started

1. Fork the repository on GitHub
2. Clone the forked repository to your local machine
3. Install the tooling with `pip install -r requirements-dev.txt`
4. Start doing your changes
5. Run `pytest` and `ruff check .` — both must pass
6. Commit and push your changes to your forked repository
7. Create a pull request to the original repository
8. Wait for the pull request to be reviewed and merged
9. Celebrate 🎉

`requirements-dev.txt` holds only what the tests and the linter need.
`requirements.txt` holds what the executables need at runtime, and is what to
install to build with `pyinstaller build.spec` (Windows only).

## Running the code

Requires Python 3.11+. The test suite runs on any platform; building the
executables only works on Windows.

```sh
pip install -r requirements-dev.txt   # test + lint tooling
pytest                                # run the suite
ruff check . && ruff format .         # lint and format
```

To run the presence from source, put a **non-binary** `.hoi4` save in
`src/save games/` (there is a sample there already), make sure Discord is
running, then:

```sh
python src/entrypoints/hoi4RPC.py
```

It reports the newest save in that folder, as long as it was modified in the last
two minutes, and exits once `hoi4.exe` is no longer running.

To build the executables and the release zip, on Windows:

```sh
pip install -r requirements.txt
pyinstaller build.spec
```

[docs/architecture.md](docs/architecture.md) explains how the pieces fit
together. [AGENTS.md](AGENTS.md) documents the repository layout and the
constraints the code has to work within — worth reading before a larger change.

## Attention after your changes

1. **Tests and lint pass.** `pytest` and `ruff check .`, plus `ruff format .` to
   apply formatting. CI runs all three and blocks the release build if any fail.
2. **New logic comes with a test.** The pure, testable parts live in
   `src/hoi4presence/`; the scripts in `src/entrypoints/` stay thin enough that
   they need no tests of their own beyond the structural ones in
   `tests/test_packaging.py`.
3. **Update the docs** for anything a user or a contributor sees: `readme.md` for
   behaviour and settings, `docs/architecture.md` for the flow.
4. **Add a `CHANGELOG.md` entry** under `Unreleased`.

## Versioning and releases

The versioning scheme is [SemVer](https://semver.org/). The version lives in
exactly one place: **`version.json` at the repository root**. `build.spec` reads
it to name the release zip, and the updater compares it against the published
copy. Do not duplicate it anywhere else.

To bump a version: edit `version.json`, move the `Unreleased` entries in
`CHANGELOG.md` under the new version, and open a PR.

Release lanes:

| Branch | Result |
| --- | --- |
| `main` | rolling `beta` prerelease, "Beta release" |
| `dev` | rolling `dev` prerelease, "Testers build", also runnable via *Run workflow* |

Both build workflows depend on the test workflow, so a red suite never ships.
Stable `vX.Y.Z` releases are still tagged by hand. The tag must be exactly
`v<version>` — the auto-updater looks for an asset named
`hoi4-presence-v<version>.zip` and silently finds nothing if it differs.

Push to `dev` whenever you change `build.spec`, the entry-point scripts, or the
package layout: that lane is the only thing that proves the Windows build still
works.
