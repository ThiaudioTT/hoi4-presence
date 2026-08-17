<h1 align="center">
Hoi4 Rich Presence
</h1>

<div align="center">

[![Download - Latest Release](https://img.shields.io/badge/Download-Latest_Release-2ea44f?style=for-the-badge)](https://github.com/ThiaudioTT/hoi4-presence/releases/latest)

![demonstration](docs/demo.PNG)

![WindowsOnly](https://img.shields.io/badge/Only-blue?logo=Windows&style=flat&label=Windows)
[![Build](https://github.com/ThiaudioTT/hoi4-presence/actions/workflows/build-release-python.yaml/badge.svg)](https://github.com/ThiaudioTT/hoi4-presence/actions/workflows/build-release-python.yaml)
![GithubStars](https://img.shields.io/github/stars/thiaudiott/hoi4-presence?logo=github)
![GithubIssues](https://img.shields.io/github/issues/thiaudiott/hoi4-presence?logo=github)
![GitHub last commit](https://img.shields.io/github/last-commit/thiaudiott/hoi4-presence?logo=github)

<!-- DEPENDENCIES -->
[![pypresence](https://img.shields.io/badge/using-pypresence-00bb88.svg?logo=discord&logoWidth=20)](https://github.com/qwertyquerty/pypresence)
[![Pyinstaller](https://img.shields.io/badge/using-pyinstaller-00bb88.svg?logo=python)](https://github.com/pyinstaller/pyinstaller)

<!-- MEME -->
![BuiltWithSwag](http://ForTheBadge.com/images/badges/built-with-swag.svg)
![MadeWithPython](http://ForTheBadge.com/images/badges/made-with-python.svg)

</div>

## About

This is a presence for discord that shows what you are doing in Hearts of Iron 4.

## How to download and install

Struggling in installing? See the [Wiki](https://github.com/ThiaudioTT/hoi4-presence/wiki/Downloading,-Installing-and-Uninstalling).

Briefly: download the latest release, unzip it, and run `setup.exe`. The installer

- copies the presence into `Documents\Paradox Interactive\Hearts of Iron IV\hoi4Presence`,
- sets `save_as_binary=no` in the game's `settings.txt`, because the presence reads your
  autosaves and can only do that when they are plaintext,
- drops `runRPC.exe` and `runRPC.cfg` into your game folder, and
- points the Paradox launcher at `runRPC.exe`, which starts the game and the presence together.

Run `uninstall.exe` to reverse all of that.

## Known issues

HOI4 is frequently updating, see known issues in [Issues](https://github.com/ThiaudioTT/hoi4-presence/labels/bug).

## Submiting an issue

Found a bug? [Submit it](https://github.com/ThiaudioTT/hoi4-presence/issues/new/choose).

If the presence is not showing up, attach `hoi4Presence.log` and
`checkupdate.log` from the `hoi4Presence` folder in your documents directory.
The first records why no save was read or why Discord could not be reached, the
second why an update was skipped.

## Contributing

Feel free to contribute! I will be happy to see your pull request.

First, read the [CONTRIBUTING.md](CONTRIBUTING.md) file.

## how the presence works?

It uses the saves to get data. So, spend one month in the game or save the game to update the presence.

See: [How it Works](https://github.com/ThiaudioTT/hoi4-presence/wiki/How-it-works), and
[docs/architecture.md](docs/architecture.md) for the developer-facing version.

## Settings

`version.json`, next to the executables, holds the only user-tunable setting:

```json
{
    "version": "1.3.0",
    "auto-update": true
}
```

Set `auto-update` to `false` to stop the presence updating itself when a newer
release is published. Do not edit `version`; the updater compares it against the
published one.

## Development

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

See [AGENTS.md](AGENTS.md) for the repository map and the constraints to work within.

## Image sources

[Hoi4 Wiki](https://hoi4.paradoxwikis.com/Hearts_of_Iron_4_Wiki)

[Logo](https://www.reddit.com/r/hoi4/comments/85l962/new_game_icon_made_by_me_the_original_sucks_free/)
