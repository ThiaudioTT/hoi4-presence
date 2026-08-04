# Autosaves

Save files used when running the presence from a source checkout. Installed, the
presence reads the real HOI4 save folder instead; both resolve as
`../save games/` relative to the running program.

There's an example save game in this folder — the real thing is enormous, so this
is trimmed to just the header the presence actually reads.

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
