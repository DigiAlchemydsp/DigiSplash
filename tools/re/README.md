# tools/re

The reverse-engineering and capture instruments that produced the addresses in
[docs/TECHNICAL.md](../../docs/TECHNICAL.md) and the mods. You do **not** need
these to build or install a mod — they are for finding the same addresses on a
new firmware, or capturing the intro from the emulator.

They import a **digiemu** checkout (patched Unicorn) or an **elekloader**
checkout. Point `DIGIEMU_DIR` / `ELEKLOADER_DIR` at them, or keep those
checkouts next to this repo (the tools look for them by name).

| file | needs | what |
|---|---|---|
| `dt1.py` | capstone | disassemble/dump a decompressed main OS. `DT1_IMG` sets the image (default `section_3_MAIN_OS.bin`). `disas`, `hex`, `word`, `render` |
| `capture_splash.py` | digiemu | resume a pre-intro snapshot, deliver PIT3, write a PNG at each present (the composed frame) |
| `cold_capture.py` | digiemu | capture from a cold boot, polling the panel buffer |
| `capture_intro.py` | digiemu | capture at the PIT3 ISR |
| `patch.py` | elekloader | standalone Digitakt `rare` / `reveal` patcher (the mods are preferred now) |
| `_paths.py` | — | locates the checkouts for the others |

## Disassemble

```sh
export DT1_IMG=section_3_MAIN_OS.bin      # a decompressed main OS (elekloader .section(3))
python dt1.py disas 0x4006c2f4 --until 0x4006c300 --notes
python dt1.py hex 0x400e60e2 --len 12
```

Find the selector and the intro present calls yourself by scanning for
`0c80 0000 7fdf` (`cmpi.l #$7fdf,d0`) and `4eb9 <present>`.

## Capture

The capture tools use digiemu's `emu` package and expect its `DT2_*` paths set
to a firmware folder (`DT2_SYX`, `DT2_SECTIONS`, `DT2_SNAPSHOTS`,
`DT2_PLUSDRIVE`, `DT2_MAIN_IMG`). A pre-intro `boot.snap` is needed; make one
with `python -m emu.portable --add <build>.syx --yes --home <dir>`.

Digitakt mk1 1.53 defaults are built in; the Digitone 1.43 addresses are:

```sh
python capture_splash.py --syx F.syx --snapshot boot.snap --out frames \
    --fb-front 0x40241a44 --diff-body 0x400f8f02 --flush-body 0x400f8e84 \
    --intro-done 0x40091aea
```

| device | `--fb-front` | `--diff-body` | `--flush-body` | `--intro-done` |
|---|---|---|---|---|
| Digitakt 1.53 | `0x4020d8f8` | `0x400e60ea` | `0x400e606c` | `0x4006cb94` |
| Digitone 1.43 | `0x40241a44` | `0x400f8f02` | `0x400f8e84` | `0x40091aea` |

The `--*-body` addresses are the present entries plus 8 (after the displaced
prologue), i.e. after any splash mod has drawn.
