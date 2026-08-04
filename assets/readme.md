# Assets Art

A mirror of the flag images uploaded to the Discord developer portal, kept here
so the set is reviewable in the repository. **Nothing in the code reads this
folder** — at runtime Discord is given the asset *key*, and Discord serves the
image it has on file.

That means adding a PNG here is only half the job:

1. upload the image to the Discord developer portal for this application, and
2. add the PNG here with a filename equal to the portal's asset key, which by
   convention is the lowercased country tag (`GER` → `ger.png`), and
3. reference that key in `countries` in `src/hoi4presence/countries.py`.

`tests/test_countries_data.py` checks both directions: every asset key used by a
country has a PNG here, and every PNG here is referenced by a country. A flag
that is not on the portal should use a full `https://` URL in `countries.py`
instead, with no file here.

Not mirrored: `hoi4-logo` and `hoi4-logo2`, the application's own artwork, which
exist only on the portal.

See [AGENTS.md](../AGENTS.md) for the full rules on adding a country.
