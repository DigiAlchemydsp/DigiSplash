# custom-splash (Digitone mk1 / Keys, OS 1.43)

Draws **your own 128x64 image** as the Digitone boot splash. Needs `core`
(core-dn1); combines with other mods.

## How it works

At each of the intro's panel-present call sites it copies `splash.bin` (1024
bytes, the panel format) over the frame the intro just composed, then runs the
stock present. It gates on the intro still owning PIT3, so nothing is drawn
over the UI. The panel format is the same as the Digitakt's — see
[../../../docs/PANEL-FORMAT.md](../../../docs/PANEL-FORMAT.md).

## Make an image

```sh
python mksplash.py logo.png splash.bin        # or --text "HELLO", --invert, --dither
```

## Build and install

```sh
cd elekloader
python -m elekloader.sdk.build ../digitakt-splash-mods/digitone1/mods/custom-splash \
    --stock Digitone_and_Digitone_Keys_OS1.43.syx
python -m elekloader.patch --stock Digitone_and_Digitone_Keys_OS1.43.syx \
    --mod mods/core-dn1/out/core-dn1-2.0a.elemod \
    --mod ../digitakt-splash-mods/digitone1/mods/custom-splash/out/custom-splash-1.0.elemod \
    --out custom-dn1.syx --version 2.0s
```
