# Autosaves

Save files used when running the presence from a source checkout. Installed, the
presence reads the real HOI4 save folder instead; both resolve as
`../save games/` relative to the running program.

The example save games in this folder are trimmed to just the header the presence
reads — the real thing is around 50 MB, because the rest of it is the world state.

Between them they cover every difficulty, every ideology and both ironman states,
and the filenames record which difficulty each campaign was started on, which is
what `tests/test_presence.py` checks the difficulty table against:

| file | difficulty | ideology | ironman |
| --- | --- | --- | --- |
| `civilian-france.hoi4` | Civilian | Democratic | |
| `recruit-japan.hoi4` | Recruit | Non-Aligned | |
| `regular-sov.hoi4` | Regular | Communist | |
| `usa-veteran.hoi4` | Veteran | Democratic | |
| `ger-elite.hoi4` | Elite | Fascist | |
| `tibet-ironman-elite.hoi4` | Elite | Non-Aligned | yes |
| `GER_1936_01_01_12.hoi4` | Regular | Fascist | (an older patch) |

The presence only reads the **most recently modified** one, so `touch` whichever
you want to see.

You can generate your own by saving with `save_as_binary=no` in the game's
`settings.txt` and dropping the file here.

Two things to remember when testing:

- the save must have been **modified in the last two minutes**, otherwise it is
  treated as left over from a previous session and skipped. `touch` it if needed.
- the presence polls every 30 seconds, and exits once `hoi4.exe` is no longer
  running — so from a source checkout it will stop after one cycle unless the
  game is open.

Run it with:

```sh
python src/entrypoints/hoi4RPC.py
```

Check `hoi4Presence.log` next to the entry point if nothing shows up.

> ``Hint``: You can edit the code and not lose time to test.
