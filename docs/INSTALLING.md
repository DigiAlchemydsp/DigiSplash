# Installing (building a flashable .syx)

A splash mod is combined with `core` by `elekloader.patch`, which writes a new
OS `.syx`, checks it, and prints the resulting hashes.

```sh
cd elekloader
CORE=mods/core/out/core-2.1.elemod
MODS=../digitakt-splash-mods/mods

python -m elekloader.patch --stock Digitakt_OS1.53.syx \
    --mod "$CORE" \
    --mod "$MODS/digitussy/out/digitussy-1.0.elemod" \
    --out digitussy.syx --version 2.0s
```

Expect, at the end:

```
verified: sections 2, 4, 5, 8, byte for byte; the main OS depacks to the
patched image in place (min gap … bytes); flash ends 0x… (… bytes spare)
WROTE digitussy.syx
```

`--version XXXX` sets the four characters the unit shows. You can pass
several `--mod`s; `patch` refuses overlaps, so you will know if two mods
cannot live together.

## Which mods combine

| can be installed with | and |
|---|---|
| `core` | always required |
| `custom-splash` | any other (non-conflicting) mod |
| `digitussy` | anything **except** `digitrash` and `rare-splash` |
| `digitrash` | anything **except** `digitussy` and `rare-splash` |
| `rare-splash` | anything **except** `digitussy` and `digitrash` |

`digitussy`, `digitrash` and `rare-splash` all patch `0x4006c2fa` or the
intro's present calls, so they overlap; pick one splash.

## Flashing and recovery

- Send the `.syx` to the unit with Elektron Transfer (MIDI/SysEx), the same
  way a stock OS is installed.
- **Recovery:** hold `FUNC` while powering on for the startup menu, then
  choose OS UPGRADE and send the stock `Digitakt_OS1.53.syx`. Keep the stock
  file.
- Only the main OS section changes, so the bootstrap and updater stay stock.

## Changing the custom-splash image

`custom-splash` draws `mods/custom-splash/splash.bin`. Replace it and rebuild:

```sh
python mksplash.py your-logo.png splash.bin     # see docs/PANEL-FORMAT.md
cd elekloader
python -m elekloader.sdk.build ../digitakt-splash-mods/mods/custom-splash --stock Digitakt_OS1.53.syx
python -m elekloader.patch --stock Digitakt_OS1.53.syx \
    --mod mods/core/out/core-2.1.elemod \
    --mod ../digitakt-splash-mods/mods/custom-splash/out/custom-splash-1.0.elemod \
    --out custom.syx --version 2.0c
```

## Verifying a build without hardware

`digiemu` boots the firmware and compares the screen and audio with stock. A
splash mod keeps every other screen identical and only changes the intro, so
it passes a screen comparison as long as the UI still comes up — which it does
for all four mods. The captures in [`../screenshots`](../screenshots) are from
that emulator.
