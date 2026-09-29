# Building the .elemods

Each mod is a folder under `mods/` with a `mod.json`. It is built to a
`.elemod` by elekloader's SDK. The mods target **Digitakt mk1 OS 1.53** by
section hash, so you need the exact stock file the profile names.

## What you need

- An **elekloader** checkout (`elekloader/`) and Python 3.9+.
- The stock **`Digitakt_OS1.53.syx`**, lawfully obtained. elekloader checks it
  by SHA-256: `9bdd44bb…cc92`.
- The **m68k toolchain**, for every mod with sources. `rare-splash` has none
  and builds without a toolchain.

### Toolchain

The SDK calls `<prefix>gcc`, `<prefix>as` and `<prefix>ld`, where `<prefix>`
comes from the device profile (`m68k-linux-gnu-`) unless `ELEKLOADER_CROSS`
overrides it.

| where you are | install | use |
|---|---|---|
| Debian/Ubuntu | `apt install binutils-m68k-linux-gnu gcc-m68k-linux-gnu` | leave `ELEKLOADER_CROSS` unset |
| Windows (this machine) | `C:\sysgcc\m68k-elf` (GCC 4.8.0) | `ELEKLOADER_CROSS=m68k-elf-` and put `C:\sysgcc\m68k-elf\bin` on `PATH` |

```sh
# Windows / Git Bash
export ELEKLOADER_CROSS=m68k-elf-
export PATH=/c/sysgcc/m68k-elf/bin:$PATH
```

**Gotcha.** The SDK's assembler flags include `-mcpu=54455`. Binutils built
against that CPU variant accepts `-mcpu=54455`, but the Windows m68k-elf gas
does **not** decode `dbra` under it. The sources here avoid `dbra` and loop
with `subq`/`bne` instead, so both toolchains assemble them. If you add code,
keep that in mind.

## Build

From the elekloader checkout, with `Digitakt_OS1.53.syx` in the working
directory:

```sh
python -m elekloader.sdk.build ../digitakt-splash-mods/mods/rare-splash  --stock Digitakt_OS1.53.syx
python -m elekloader.sdk.build ../digitakt-splash-mods/mods/digitussy    --stock Digitakt_OS1.53.syx
python -m elekloader.sdk.build ../digitakt-splash-mods/mods/digitrash    --stock Digitakt_OS1.53.syx
python -m elekloader.sdk.build ../digitakt-splash-mods/mods/aba-bootanim --stock Digitakt_OS1.53.syx
```

Expect:

```
BUILT …/mods/<id>/out/<id>-1.0.elemod
  <id> 1.0: .run N, .fast 0, .bss N bytes; K sites, R relocations; imports nothing
```

`--out DIR` writes elsewhere. A failure prints `BUILD FAILED: …`; the message
names the site or source.

## Check it

`lint` links the mod with the mods it needs and refuses overlaps, bad sites,
missing imports or over-budget memory:

```sh
CORE=elekloader/mods/core/out/core-2.1.elemod      # your core build

python -m elekloader.lint ../digitakt-splash-mods/mods/rare-splash/out/rare-splash-1.0.elemod \
    --stock Digitakt_OS1.53.syx --with "$CORE"
# OK: links as core 2.1 > rare-splash 1.0; RAM … of 131072 bytes
```

Every mod here needs `core`. `lint` without it prints
`core is not enabled, and every other mod builds on it`.

## What the SDK does

`python -m elekloader.sdk.build`:

1. reads `mod.json`, checks `device`/`os` against the stock file and the
   stock bytes at every `sites` entry;
2. assembles/compiles `sources` with the device flags, `ld -r`'s them into
   one object, and keeps `.run`, `.fast`, `.bss` (see elekloader's
   `docs/FORMAT.md`, at
   [github.com/irpina/elekloader](https://github.com/irpina/elekloader));
3. stores runs of your bytes that also occur in the firmware as *references*
   to the user's own image, never as shipped bytes;
4. relocates it and validates the result with the linker.

A code site must cover **whole stock instructions**; `lint` and the build both
check that. `op` in `sites` is `jsr`/`jmp` (call/jump a symbol), `keep2`,
`ptr`, or `bytes` (raw `new`, with `"kind": "code"` for instructions).

## A whole build instead (no toolchain combination)

If you would rather ship one monolithic firmware as a format-1 mod, build the
`.syx` however you like and let elekloader turn it into one:

```sh
python -m elekloader.mkmod --stock Digitakt_OS1.53.syx --build my-cfw.syx \
    --diff --meta meta.json --out my-cfw.elemod
```

Format-1 mods cannot be combined with anything else; the splash mods here are
format 2 for that reason. See `elekloader/docs/ADAPTING.md`.
