# Digitakt mk1 splash mods

Boot-splash mods for the Elektron **Digitakt mk1** (OS 1.53), built for
[elekloader](../elekloader). They change only the main OS section, need the
`core` mod, and can be combined with other non-conflicting mods. No Elektron
firmware is included.

![DigiTussy](screenshots/digitussy.gif)
![DigiTrash](screenshots/digitrash.gif)

| mod | what it does | sources |
|---|---|---|
| [`custom-splash`](mods/custom-splash) | draws **your own 128x64 image** as the splash; `mksplash.py` converts a PNG to the panel format | asm |
| [`rare-splash`](mods/rare-splash) | boots on the **alternate** stock animation, the one the unseeded selector never reaches | 1 instruction |
| [`digitussy`](mods/digitussy) | animated: the **DIGITUSSY** wordmark bobbing over rising particles | C + asm |
| [`digitrash`](mods/digitrash) | animated: the **DIGITRASH** wordmark and a trash can with six flying flies | C + asm |

![usual vs rare](screenshots/usual-vs-rare.png)

*(left: the usual boot animation, ~367 lit pixels — right: the rare one,
~666; both captured from a real 1.53 image in digiemu.)*

`custom-splash`, `digitussy` and `digitrash` draw over the intro; `rare-splash`
changes which stock animation runs. `digitussy`, `digitrash` and `rare-splash`
all touch the same instruction, so install **one of them** (they overlap);
`custom-splash` can go with either.

## Quick start

```sh
# 1. build the .elemods (needs elekloader and the m68k toolchain; see docs/BUILDING.md)
cd elekloader
python -m elekloader.sdk.build ../digitakt-splash-mods/mods/digitussy --stock Digitakt_OS1.53.syx

# 2. build a flashable firmware with core and the mod (see docs/INSTALLING.md)
python -m elekloader.patch --stock Digitakt_OS1.53.syx \
    --mod mods/core/out/core-2.1.elemod \
    --mod ../digitakt-splash-mods/mods/digitussy/out/digitussy-1.0.elemod \
    --out digitussy.syx --version 2.0s
```

`digitussy` and `digitrash` need the m68k toolchain (they have C sources).
`rare-splash` and `custom-splash`'s site work needs it too, because
`custom-splash` has assembly; **only `rare-splash` builds without a toolchain**
(it has no sources).

## Documentation

| | |
|---|---|
| [docs/BUILDING.md](docs/BUILDING.md) | the toolchain, `sdk.build`, `lint`, and how a `.elemod` is checked |
| [docs/INSTALLING.md](docs/INSTALLING.md) | `elekloader.patch`, flashing, recovery, which mods conflict |
| [docs/PANEL-FORMAT.md](docs/PANEL-FORMAT.md) | the 128x64 1bpp panel layout and how to make art for it |
| [docs/TECHNICAL.md](docs/TECHNICAL.md) | how the intro selects and presents, and where each mod hooks |
| [NOTICE.md](NOTICE.md) | licence and the independence statement |

## Layout

```
mods/<id>/mod.json     the mod (elekloader format 2)
mods/<id>/*.s,*.c      sources
mods/<id>/out/         build output (gitignored)
screenshots/           captured in digiemu
docs/                  the guides above
```

## Licence

The mods are GPL-2.0-or-later (see [LICENSE](LICENSE)). Digitakt and Elektron
are trademarks of their respective owners; this project is independent and is
not affiliated with or endorsed by Elektron.
