# make-bootanim

Turn a **PNG or GIF** into a boot-splash mod for the Digitakt mk1 (OS 1.53) or
Digitone mk1 / Keys (OS 1.43).

![example](../../screenshots/bootanim-example.gif)

It writes a ready-to-build elekloader mod folder: the frames packed to the
128x64 panel format, an assembly stub that cycles them at the intro's panel
presents, and a `mod.json` with the device's sites. You then build and patch
it with elekloader like any other mod.

## Use

```sh
tools\make-bootanim\make-bootanim.bat hamster.gif
tools\make-bootanim\make-bootanim.bat logo.png --name "My logo"
tools\make-bootanim\make-bootanim.bat anim.gif --dn -o my-dn-anim --frames 40
```

| option | |
|---|---|
| `-o DIR` | output mod folder (default `<name>-bootanim`) |
| `--name NAME` | mod name and title (default from the file) |
| `--dn` | Digitone mk1 / Keys (1.43) instead of Digitakt mk1 (1.53) |
| `--frames N` | keep at most N frames, evenly spaced (default 60) |
| `--invert` | swap ink and paper (the panel lights the 1 bits) |
| `--dither` | Floyd-Steinberg instead of a hard threshold |
| `--text STR` | render text with a built-in font instead of an image |

Needs Python 3 with Pillow (`python -m pip install pillow`). The `.bat` finds
`python` or `py` on PATH; you can also run `make_bootanim.py` directly.

## Build and install

```sh
cd elekloader

# Digitakt
python -m elekloader.sdk.build <outdir> --stock Digitakt_OS1.53.syx
python -m elekloader.patch --stock Digitakt_OS1.53.syx \
    --mod mods/core/out/core-2.1.elemod \
    --mod <outdir>/out/<id>-1.0.elemod --out my-bootanim.syx --version 2.0x

# Digitone (--dn)
python -m elekloader.sdk.build <outdir> --stock Digitone_and_Digitone_Keys_OS1.43.syx
python -m elekloader.patch --stock Digitone_and_Digitone_Keys_OS1.43.syx \
    --mod mods/core-dn1/out/core-dn1-2.0a.elemod \
    --mod <outdir>/out/<id>-1.0.elemod --out my-bootanim-dn.syx --version 2.0x
```

`<id>` is the name lowercased with non-alphanumerics turned into `-`.

## Notes

- The intro presents about 15 frames a second, so one frame per present is
  roughly 15 fps. Use `--frames` to keep a GIF short enough (each frame is
  1 KB; the RAM budget is 128 KB).
- Frames are scaled to fit 128x64 preserving aspect, centred on black.
- The generated mod draws over the composed intro frame and gates on the
  intro still owning PIT3, so it does nothing to the user interface.
- It needs `core` (or `core-dn1`) and cannot be combined with the hand-written
  splash mods (they patch the same sites).
- Colour is discarded; the panel is 1 bit per pixel. See
  [`../../docs/PANEL-FORMAT.md`](../../docs/PANEL-FORMAT.md).
