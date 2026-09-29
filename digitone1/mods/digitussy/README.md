# digitussy (Digitone mk1 / Keys, OS 1.43)

An animated boot splash: the **DIGITUSSY** wordmark bobbing over a field of
rising particles, with a flickering underline. Needs `core` (core-dn1).

![digiTussy on the Digitone](../../../screenshots/digitussy-dn1.gif)

## How it works

The same `render.c` as the Digitakt mod, retargeted to the Digitone's panel
buffer (`0x40241a44`) and intro handler (`0x40090cdc`). It draws every frame at
the intro's panel-present call sites, over the frame the intro just composed,
and gates on the intro still owning PIT3 so the UI is untouched.

## Build and install

Needs the m68k toolchain (see [../../../docs/BUILDING.md](../../../docs/BUILDING.md)).

```sh
export ELEKLOADER_CROSS=m68k-elf-
export PATH=/c/sysgcc/m68k-elf/bin:$PATH
cd elekloader
python -m elekloader.sdk.build ../digitakt-splash-mods/digitone1/mods/digitussy \
    --stock Digitone_and_Digitone_Keys_OS1.43.syx
python -m elekloader.patch --stock Digitone_and_Digitone_Keys_OS1.43.syx \
    --mod mods/core-dn1/out/core-dn1-2.0a.elemod \
    --mod ../digitakt-splash-mods/digitone1/mods/digitussy/out/digitussy-1.0.elemod \
    --out digitussy-dn1.syx --version 2.0s
```

Install only one of `digitussy`, `digitrash` and `rare-splash` (they overlap).
