# custom-splash

Draws **your own 128x64 image** as the boot splash. Needs `core`; combines
with other mods.

![custom splash](../../screenshots/custom-splash.png)

## How it works

At each of the intro's panel-present call sites it copies `splash.bin` (1024
bytes, the panel format) over the frame the intro just composed, then runs
the stock present. See [../../docs/TECHNICAL.md](../../docs/TECHNICAL.md) and
[../../docs/PANEL-FORMAT.md](../../docs/PANEL-FORMAT.md).

It gates on the intro still owning PIT3, so nothing is drawn over the UI.

## Make an image

```sh
python mksplash.py logo.png splash.bin        # or --text "HELLO", --invert, --dither
```

## Build and install

```sh
cd elekloader
python -m elekloader.sdk.build ../digitakt-splash-mods/mods/custom-splash --stock Digitakt_OS1.53.syx
python -m elekloader.patch --stock Digitakt_OS1.53.syx \
    --mod mods/core/out/core-2.1.elemod \
    --mod ../digitakt-splash-mods/mods/custom-splash/out/custom-splash-1.0.elemod \
    --out custom.syx --version 2.0c
```
