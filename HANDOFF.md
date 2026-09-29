# HANDOFF

State of the **DigiSplash** repo and how to pick it up. Two devices, four
hand-written splash mods each side, plus a generator, docs and screenshots.

- Remote: <https://github.com/DigiAlchemydsp/DigiSplash> (public, `main`)
- Local: `C:\Users\benan\Music\ELEKTRON\digitakt-splash-mods`
- Built for [elekloader](../../elekloader) (elekloader's own checkout is at
  `C:\Users\benan\Music\ELEKTRON\elekloader`).

## Repo map

```
mods/<id>/                Digitakt mk1 (OS 1.53) mods
digitone1/mods/<id>/      Digitone mk1 / Keys (OS 1.43) mods
tools/make-bootanim/      PNG/GIF -> splash mod generator (bat + py)
docs/                     BUILDING, INSTALLING, PANEL-FORMAT, TECHNICAL
screenshots/              captures from digiemu
NOTICE.md, LICENSE        independence statement; GPL-2.0
```

Committed mods: `custom-splash`, `rare-splash`, `digitussy`, `digitrash`, and
the generated example `aba-bootanim` (both devices). `tools/make-bootanim/aba.gif`
is the source the example was made from.

## What each mod is

| mod | mechanism |
|---|---|
| `custom-splash` | copies a fixed 1024-byte `splash.bin` over each composed intro frame |
| `rare-splash` | NOPs the selector branch so the alternate stock animation runs (1 instruction) |
| `digitussy` | `render.c`: bobbing wordmark + rising particles, drawn every frame |
| `digitrash` | `render.c`: wordmark + trash can + six wandering flies |
| `aba-bootanim` | generated: cycles N frames from `frames.bin` |

The **draw mods** (`custom-splash`, `digitussy`, `digitrash`, `aba-bootanim`)
all hook the same intro present call sites, so they are mutually exclusive.
**`rare-splash` patches a different instruction and combines with any of them**
— but a draw mod paints the whole frame, so when combined `rare-splash` is
composed and then overwritten: it is invisible. Install `rare-splash` alone to
see the alternate stock animation. (Verified: `rare-splash + digitussy` lints
OK; `digitussy + custom-splash` overlaps.)

## Firmware addresses

Digitakt mk1 1.53 (`Digitakt_OS1.53.syx`, section 3, loads at `0x40000400`):

| | |
|---|---|
| intro task / selector `cmpi.l #$7fdf` | `0x4006c2ae` / `0x4006c2f4` |
| selector branch (`ble`, rare-splash) | `0x4006c2fa` (`6f0000d6` -> `4e714e71`) |
| RNG / state / (uncalled) srand | `0x40105910` / `0x406481e8` / `0x4010595a` |
| delta present / full present | `0x400e60e2` / `0x400e6064` |
| delta call sites | `0x4006c2d0`, `0x4006c3ac`, `0x4006c864`, `0x4006cb68` |
| full call sites | `0x4006c3a4`, `0x4006c85c`, `0x4006cb60` |
| `fb_front` / `fb_back` globals | `0x4020d8f8` / `0x4020d8fc` |
| PIT3 vector slot / intro ISR / intro_done | `0x40000340` / `0x4006c154` / `0x4006cb94` |
| core mod | `elekloader/mods/core/out/core-2.1.elemod` |

Digitone mk1 1.43 (`Digitone_and_Digitone_Keys_OS1.43.syx`):

| | |
|---|---|
| selector `cmpi.l #$7fdf` / branch | `0x40090e7c` / `0x40090e82` (`6f0001a2` -> `4e714e71`) |
| RNG / state | `0x401175e0` / `0x40554fe4` |
| delta present / full present | `0x400f8efa` / `0x400f8e7c` |
| delta call sites | `0x40090e58`, `0x40091000`, `0x4009130a`, `0x400917bc`, `0x40091ac0` |
| full call sites | `0x40090ff8`, `0x40091302`, `0x400917b4`, `0x40091ab8` |
| `fb_front` global | `0x40241a44` |
| intro ISR / intro_done | `0x40090cdc` / `0x40091aea` |
| core mod | `elekloader-main/build/cores/core-dn1-2.0a.elemod` |

Details in [docs/TECHNICAL.md](docs/TECHNICAL.md) and
[digitone1/README.md](digitone1/README.md).

## Build

```sh
export ELEKLOADER_CROSS=m68k-elf-
export PATH=/c/sysgcc/m68k-elf/bin:$PATH
cd /c/Users/benan/Music/ELEKTRON/elekloader

# Digitakt (stock in the working dir)
python -m elekloader.sdk.build ../digitakt-splash-mods/mods/digitussy --stock Digitakt_OS1.53.syx
python -m elekloader.lint   ../digitakt-splash-mods/mods/digitussy/out/digitussy-1.0.elemod \
    --stock Digitakt_OS1.53.syx --with mods/core/out/core-2.1.elemod
python -m elekloader.patch  --stock Digitakt_OS1.53.syx \
    --mod mods/core/out/core-2.1.elemod \
    --mod ../digitakt-splash-mods/mods/digitussy/out/digitussy-1.0.elemod \
    --out digitussy.syx --version 2.0s

# Digitone (same, with the Digitone stock and core-dn1)
python -m elekloader.sdk.build ../digitakt-splash-mods/digitone1/mods/digitussy \
    --stock Digitone_and_Digitone_Keys_OS1.43.syx
python -m elekloader.patch  --stock Digitone_and_Digitone_Keys_OS1.43.syx \
    --mod <core-dn1>.elemod --mod <out>/digitussy-1.0.elemod --out dn1.syx --version 2.0s
```

`rare-splash` has no sources and builds without the toolchain. Toolchain:
`C:\sysgcc\m68k-elf` (GCC 4.8.0), prefix `m68k-elf-`.

## Test in the emulator (digiemu)

`digiemu` needs its patched Unicorn; a ready venv is at
`C:\Users\benan\AppData\Local\Temp\opencode\digiemu-venv\Scripts\python.exe`
(`python -m emu.unicorn_compat` prints `compatible: true`). Run from
`C:\Users\benan\Music\ELEKTRON\digiemu-main`.

```sh
PY="C:/Users/benan/AppData/Local/Temp/opencode/digiemu-venv/Scripts/python.exe"
"$PY" -m emu.portable --add CUSTOM.syx --yes --home SOME_DIR   # first run + snapshots
```

Then capture the intro with the helper scripts (below), e.g. Digitone:

```sh
"$PY" capture_splash.py --syx <fw>/<stock>.syx --snapshot <fw>/snapshots/<name>/boot.snap \
    --out frames --fb-front 0x40241a44 --diff-body 0x400f8f02 --flush-body 0x400f8e84 \
    --intro-done 0x40091aea
```

(Digitakt defaults: `0x4020d8f8`, `0x400e60ea`, `0x400e606c`, `0x4006cb94`.)

## Helper scripts

Merged into the repo under `tools/re/` (see
[tools/re/README.md](tools/re/README.md)); they import a digiemu or elekloader
checkout via `DIGIEMU_DIR` / `ELEKLOADER_DIR`, or a checkout kept next to this
repo.

| script | what |
|---|---|
| `dt1.py` | capstone m68k disassembler + hex/word dumps; `DT1_IMG` sets the image |
| `capture_splash.py` | resume a snapshot, deliver PIT3, capture the panel frame at the present body to PNGs (per-device addresses) |
| `cold_capture.py` | cold-boot capture (polls the panel buffer) |
| `capture_intro.py` | capture at the PIT3 ISR |
| `patch.py` | standalone Digitakt `rare`/`reveal` patcher (the mods are preferred) |

The older scratch copies and the firmware/test artifacts live in
`C:\Users\benan\Music\ELEKTRON\dt1-splash` (not in the repo; they include
extracted sections, `.syx` scratch builds and emulator homes).

Extract a main OS for analysis with `elekloader.syx.Syx(<stock>).section(3)`.

## Gotchas

- **digiemu symbol scan.** Do not patch the present *functions* (their entry
  bytes are a signature for `panel_diff`/`fb_front`); hook the intro's `jsr`
  *call sites* instead. This is why the mods hook call sites.
- **`-mcpu=54455`.** The Windows m68k-elf gas rejects `dbra` under it. Loop with
  `subq`/`bne`. And `lsl.l #N` only takes 1-8, so `<<10` is two shifts.
- **SDK sites are JSON objects**, not strings (a generator bug worth
  remembering).
- **The panel is 128x64 1bpp**, `byte = page + 8*column`, `page = 7-(y>>3)`,
  `bit = y&7`. `docs/PANEL-FORMAT.md`.
- **No firmware, ever.** `.gitignore` blocks `*.syx`, `*.elemod`, `out/`,
  `*.snap`, `*.bin` (with negations for the committed `splash.bin`/`frames.bin`).
  Screenshots of the *stock* animation are Elektron's art — see `NOTICE.md`.

## Status

Tested:

- Digitakt: `digitussy`/`digitrash`/`custom-splash`/`rare-splash` build and
  lint; `digitussy`/`digitrash` cold-boot to a live UI in digiemu and their
  intro frames were captured.
- Digitone: all four build and lint against `core-dn1` 2.0a; `digitussy` and
  the generated `aba` build cold-boot to a live UI with the FM DSP running
  (`dsp_running_u32=0x2`), and their frames were captured.
- `tools/make-bootanim`: a 6-frame GIF builds/lints/patches for the Digitakt
  and cycles in digiemu; a PNG builds for the Digitone.

## Open / next

- `aba-bootanim` has not been cold-booted on the **Digitakt** (the Digitone
  twin has). Cheap to check.
- No capture of the **Digitone `rare-splash`** alternate animation.
- `.fast`/SRAM is unused; frames for a long GIF could be budgeted better
  (each frame is 1 KB; RAM budget is 128 KB).
- Nothing is flashed on the physical units from this session's builds.
