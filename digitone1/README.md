# Digitone mk1 / Digitone Keys (OS 1.43)

The same splash mods, ported to the **Digitone mk1 and Digitone Keys** (one OS
file serves both), built for elekloader's `core-dn1`, plus the generated
example. The panel is the same 128x64 mono screen, so the graphics and the panel
format are identical to the Digitakt's — only the firmware addresses differ.

![DigiTussy on the Digitone](../screenshots/digitussy-dn1.gif)

| mod | what it does |
|---|---|
| [`rare-splash`](mods/rare-splash) | boots the alternate stock animation, the one the unseeded selector never reaches |
| [`digitussy`](mods/digitussy) | animated wordmark + rising particles |
| [`digitrash`](mods/digitrash) | animated wordmark, trash can and flies |
| [`aba-bootanim`](mods/aba-bootanim) | example animated GIF from `make-bootanim` |

As on the Digitakt, the draw mods (`digitussy`, `digitrash` and
`aba-bootanim`) hook the same present sites, so install **one** of them;
`rare-splash` patches a different instruction and combines with any of them.

## Digitone addresses (OS 1.43)

The intro is the Digitakt's code, relinked. For reference:

| | Digitakt 1.53 | Digitone 1.43 |
|---|---|---|
| intro task / selector compare | `0x4006c2f4` | `0x40090e7c` |
| selector branch (`ble`) | `0x4006c2fa` | `0x40090e82` |
| RNG (`rand`) | `0x40105910` | `0x401175e0` |
| RNG state | `0x406481e8` | `0x40554fe4` |
| panel delta present | `0x400e60e2` | `0x400f8efa` |
| panel full present | `0x400e6064` | `0x400f8e7c` |
| `fb_front` pointer global | `0x4020d8f8` | `0x40241a44` |
| intro PIT3 handler | `0x4006c154` | `0x40090cdc` |
| intro exit (`intro_done`) | `0x4006cb94` | `0x40091aea` |

The six intro present-call sites the draw mods hook are
`0x40090e58`, `0x40091000`, `0x4009130a`, `0x400917bc`, `0x40091ac0`
(delta) and `0x40090ff8`, `0x40091302`, `0x400917b4`, `0x40091ab8` (full).

## Build

The Digitone stock is `Digitone_and_Digitone_Keys_OS1.43.syx`
(SHA-256 `c5a54cc0…f9aa`).

```sh
export ELEKLOADER_CROSS=m68k-elf-
export PATH=/c/sysgcc/m68k-elf/bin:$PATH
cd elekloader
python -m elekloader.sdk.build ../digitakt-splash-mods/digitone1/mods/digitussy \
    --stock Digitone_and_Digitone_Keys_OS1.43.syx
```

`rare-splash` has no sources and builds without a toolchain. `sdk.build`
output and `lint` work the same as for the Digitakt; use the Digitone core:

```sh
python -m elekloader.lint ../digitakt-splash-mods/digitone1/mods/digitussy/out/digitussy-1.0.elemod \
    --stock Digitone_and_Digitone_Keys_OS1.43.syx --with mods/core-dn1/out/core-dn1-2.0a.elemod
```

## Install

```sh
python -m elekloader.patch --stock Digitone_and_Digitone_Keys_OS1.43.syx \
    --mod mods/core-dn1/out/core-dn1-2.0a.elemod \
    --mod ../digitakt-splash-mods/digitone1/mods/digitussy/out/digitussy-1.0.elemod \
    --out digitussy-dn1.syx --version 2.0s
```

Recovery: hold `FUNC` while powering on, press `TRIG 4` (OS UPGRADE), then
send the stock `.syx`.

Tested by cold-booting a core-dn1 + digitussy build in digiemu: it settles to
a live UI with the FM DSP running (`dsp_running_u32=0x2`), and the captured
intro frames are in [`../screenshots/digitussy-dn1.gif`](../screenshots/digitussy-dn1.gif).

See [../docs/TECHNICAL.md](../docs/TECHNICAL.md) for how the intro works, and
[../docs/PANEL-FORMAT.md](../docs/PANEL-FORMAT.md) for the image format.
