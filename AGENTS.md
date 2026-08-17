# AGENTS.md

Guidance for AI agents and new contributors working in this repository.

## What this is

A Discord Rich Presence client for Hearts of Iron IV. It polls the game's
plaintext autosaves, reads the country, ideology, year and difficulty out of the
save header, and pushes that to Discord via `pypresence`. It ships as five
PyInstaller executables.

Read [docs/architecture.md](docs/architecture.md) before changing behaviour — the
runtime chain (Paradox launcher → `runRPC.exe` → game + updater + presence) is
not obvious from the file layout.

## Repository map

| Path | What lives there |
| --- | --- |
| `src/hoi4presence/` | The library. Importable on any platform, and where tested logic belongs. |
| `src/hoi4presence/countries.py` | Tag → (name, flag) table plus `getCountry`. |
| `src/hoi4presence/saves.py` | Finding, reading and parsing save headers. |
| `src/hoi4presence/presence.py` | Builds the Discord payload dicts. No `pypresence` import. |
| `src/hoi4presence/runner.py` | The polling loop. **The only module importing `pypresence`/`psutil`.** |
| `src/hoi4presence/paths.py` | Base-directory resolution and interactive folder discovery. |
| `src/hoi4presence/logging_setup.py` | Rotating file log for the windowed executables. |
| `src/hoi4presence/ui.py` | The console wizard (`rich`) the three console executables share, plus the flag animation on setup's success screen. |
| `src/hoi4presence/updater/` | Version comparison (`version_check`), asset naming (`release`), download (`download`). |
| `src/hoi4presence/install/steps.py` | Pure transforms for `settings.txt`, `launcher-settings.json`, payload validation. |
| `src/entrypoints/` | Thin scripts PyInstaller builds. Each has a `main()` and a `__main__` guard. |
| `src/entrypoints/launcher.py` | The shim the Paradox launcher spawns. Stdlib-only, on purpose. |
| `src/save games/` | Sample save for running from source. |
| `assets/` | Mirror of the flag images uploaded to the Discord developer portal. Nothing reads it at runtime. |
| `tests/` | The pytest suite. |
| `build.spec` | PyInstaller spec plus the zip-packaging step. |
| `version.json` | The version. Single source of truth. |

## Commands

```sh
pip install -r requirements-dev.txt    # test + lint tooling (no runtime deps)
pytest                                 # the suite
ruff check . && ruff format .          # lint and format
python src/entrypoints/hoi4RPC.py      # run the presence against src/save games/
pip install -r requirements.txt        # runtime deps, needed only to build
pyinstaller build.spec                 # build the executables (Windows only)
```

## Hard constraints

**The test suite must keep running on Linux.** The product is Windows-only, but
CI runs the suite on `ubuntu-latest` and installs `requirements-dev.txt`, which
deliberately excludes `pypresence`, `psutil`, `requests` and `pyinstaller`.
So, in anything under `src/hoi4presence/` except `runner.py` and
`updater/download.py`:

- do not import those packages;
- do not read `USERPROFILE`, `PROGRAMFILES(X86)` or `TEMP` at module scope — take
  the environment as an argument, the way `paths.defaultDocumentsDir` does;
- do not assume backslash paths or a Windows filesystem in assertions.

**`rich` is in both requirements files, and pinned to 13.x.** It is the one
runtime dependency `requirements-dev.txt` also carries, because
`hoi4presence.ui` is importable, tested code and pure Python — the exclusions
above are about the Windows-only, compiled packages. The pin is not cosmetic:
rich 14+ resolves its cell-width tables through a runtime `import_module()` that
PyInstaller's static analysis cannot see, so a frozen exe raises
`ModuleNotFoundError` on the first string it measures. 13.x uses a static table
and needs no `hiddenimports`.

**The PyInstaller build cannot be verified locally** unless you are on Windows.
It only runs in CI. Any change to `build.spec`, to the entry-point script paths,
or to the package import graph must be validated by pushing to the `dev` branch
(or running *Build and release (testers)* via **Run workflow**) and checking the
resulting `dev` prerelease zip. `tests/test_packaging.py` catches the most
common breakage — `build.spec` pointing at a script that no longer exists — but
it cannot prove the build links.

**Executable names are load-bearing.** `setup.exe`, `uninstall.exe`,
`runRPC.exe`, `hoi4Presence.exe` and `checkupdate.exe` are referenced as strings
by `launcher.py`, the installer and the updater. Rename the source script if you
must; never rename the exe. `tests/test_packaging.py` pins them.

**`launcher.py` duplicates its constants deliberately.** It is the first link in
the launch chain, so it imports nothing from `hoi4presence` — nothing it needs
can then fail to import. That makes it the one place a rename in `steps.py` or
`paths.py` can silently pass;
`tests/test_packaging.py::test_the_shim_agrees_with_the_names_everything_else_uses`
is what stops it.

**`version.json` at the repository root is the only version.** `build.spec`
derives the release zip name from it and the updater compares against it. Do not
add a second copy — there used to be one in `src/checkupdate/`, and running the
updater from source would try to "upgrade" a developer's checkout.

**Entry points must stay inert on import.** All work goes in `main()` behind an
`if __name__ == "__main__"` guard. The presence used to connect to Discord and
loop at module scope, which is the reason none of this was testable.
`tests/test_packaging.py::test_entry_scripts_do_their_work_inside_main` enforces it.

## Conventions

- 4-space indentation; `ruff format` is authoritative. Config is in
  `pyproject.toml`.
- Function names are camelCase. This is not PEP 8, but it is what the codebase
  has always used, and consistency beats a mass rename.
- The windowed executables log to `hoi4Presence.log` via `logging`; the console
  executables (`setup`, `uninstall`, `checkupdate`) drive
  `hoi4presence.ui.Wizard`, because their output *is* the user interface and
  timestamps would only get in the way. Do not add bare `print` or `input` back
  to them — `Wizard.ask`/`warn` are what `paths.findDirContaining` expects, and
  `checkupdate` passes `stream=False` to `setupLogging` so its records go to
  `checkupdate.log` only.
- Prefer adding logic to `src/hoi4presence/` with a test over adding it to an
  entry-point script.

## How to add a country

Add an entry to the `countries` dict in `src/hoi4presence/countries.py`:

- if the flag has been uploaded to the Discord developer portal, use the short
  asset key (the lowercased tag) **and** add the matching PNG to
  `assets/initialCountries/`. Both are required — the tests check each direction.
- otherwise use a full `https://` image URL.

`tests/test_countries_data.py` enforces: no duplicate tags, no two countries
sharing a flag or a name (bar an explicit allowlist), asset keys equal to the
lowercased tag, and every mirrored PNG being referenced. If a new entry
legitimately reuses another country's flag, add it to `ALLOWED_SHARED_FLAGS`
with the reason rather than deleting the test.

## How to release

1. Bump `version.json`.
2. Move the `Unreleased` entries in `CHANGELOG.md` under the new version.
3. Merge to `main` — that publishes a rolling `beta` prerelease.
4. Tag a stable release **exactly** `v<version>`.

## Known follow-ups, deliberately not fixed

- **A stable release must still be tagged exactly `v<version>`.** The updater now
  fetches `/releases/tags/v{version}` using the version it read from
  `version.json` on `main`, so the rolling `beta` and `dev` prereleases
  can no longer be mistaken for an update. But the asset name is still derived
  from the tag, so a tag that is not exactly `v<version>` produces a release the
  updater will never find. `tests/test_packaging.py` pins the convention.
- **`BEG` (Benishangul-Gumuz Nation) has no flag.** It was showing Bangladesh's;
  the wiki is behind a bot challenge so the real image could not be confirmed and
  it falls back to the default logo. The likely URL is noted in a comment beside
  the entry.
- **Most wiki-hosted flags are probably not rendering.** `countries.py` has 264
  entries; 92 use a Discord developer-portal asset key and 172 use a URL. Of
  those 172, **146 point at `hoi4.paradoxwikis.com`, and every one of them now
  returns a 3 KB anti-bot challenge page instead of the PNG** — `content-type:
  text/html`, HTTP 200, even with a browser `User-Agent`. Discord fetches these
  server-side to proxy them, so those countries almost certainly show no flag.
  Reproduce with:

  ```sh
  curl -sI https://hoi4.paradoxwikis.com/images/9/9e/Bangladesh.png | grep -i content-type
  ```

  The 25 `i.imgur.com` links and the portal asset keys still serve real images.
  Fixing this means re-hosting ~146 flags — most cheaply by uploading them to
  the Discord developer portal and switching those entries to asset keys, which
  is what `test_countries_data.py` already expects for portal-hosted flags. It
  is a data migration, not a code change, so it belongs in its own PR.
