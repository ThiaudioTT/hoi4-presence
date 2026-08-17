# Ideology and ironman badges

Mirror of the small images uploaded to the Discord developer portal, the same way
`initialCountries/` mirrors the flags. Nothing reads this folder at runtime — the
presence sends the *asset key*, and Discord serves whatever is on the portal
under that name.

The file stem **is** the asset key. `presence.py` sends `header.ideology`
straight through, so these names are load-bearing:

| file / asset key | shown for |
| --- | --- |
| `fascism.png` | `ideology=fascism` |
| `democratic.png` | `ideology=democratic` |
| `communism.png` | `ideology=communism` |
| `neutrality.png` | `ideology=neutrality` |
| `anarchism.png` | `ideology=anarchism` (mods only; not in the base game) |
| `unknown-ideology.png` | any ideology with no badge of its own |
| `ironman.png` | any ironman save, in place of the ideology |

Each is 512×512, the minimum the developer portal accepts. Discord renders the
small image at roughly 24 px, so anything added here should still read when it is
essentially a thumbnail.

## Where they came from

All of them are the game's own icons, from the HOI4 wiki —
[Category:Ideology icons](https://hoi4.paradoxwikis.com/Category:Ideology_icons)
for the ideologies:

| icon | source |
| --- | --- |
| fascism | <https://hoi4.paradoxwikis.com/images/1/1f/Fascism.png> |
| democratic | <https://hoi4.paradoxwikis.com/images/e/e9/Democracy.png> |
| communism | <https://hoi4.paradoxwikis.com/images/e/e9/Communism.png> |
| neutrality | <https://hoi4.paradoxwikis.com/images/9/98/Neutrality.png> |
| anarchism | <https://hoi4.paradoxwikis.com/images/a/a8/Anarchism.png> |
| unknown-ideology | <https://hoi4.paradoxwikis.com/images/5/57/Unknown_Ideology.png> |
| ironman | <https://hoi4.paradoxwikis.com/images/c/ce/Ironman.png> |

They are Paradox's artwork, mirrored here on the same footing as the country
flags this project has always used.

Note that most wiki image URLs answer a plain `curl` with a 3 KB anti-bot
challenge page rather than the PNG — the flags in `AGENTS.md` still do. These six
paths happened to serve the real bytes with a browser `User-Agent` plus a
`Referer` header, which is worth trying first if a URL here ever needs refetching:

```sh
curl -sL -A "Mozilla/5.0 (X11; Linux x86_64) Chrome/126 Safari/537.36" \
     -H "Referer: https://hoi4.paradoxwikis.com/" \
     -o Fascism.png https://hoi4.paradoxwikis.com/images/1/1f/Fascism.png
file Fascism.png     # PNG image data, not "HTML document"
```

The wiki icons are 66×68, so they are upscaled to the portal's minimum with a
sharp bicubic filter and padded to an exact square rather than stretched:

```sh
magick Fascism.png -filter Catrom -resize 512x512 \
       -background none -gravity center -extent 512x512 -depth 8 -strip fascism.png
```

## The ironman badge

The ironman gauntlet is 25×36 and has no frame of its own, and Discord crops the
small image to a circle — so unlike the ideologies it is composited onto a dark
plate with a gold rim, which both keeps the whole icon inside the crop and
matches the wreaths the ideology icons already have:

```sh
magick -size 512x512 xc:none \
       -fill "#26241f" -stroke "#b8952f" -strokewidth 20 -draw "circle 256,256 256,28" \
       \( Ironman.png -filter Catrom -resize x330 \) -gravity center -composite \
       -depth 8 -strip ironman.png
```

After changing anything here, re-upload it to the developer portal under the same
key — the repository copy is documentation, not the thing Discord fetches.
