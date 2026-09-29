# rare-splash

Boots on the **alternate** stock animation instead of the usual one. Needs
`core`.

![rare splash](../../screenshots/rare-splash.gif)

## How it works

The intro picks between two animations from a generator that is never seeded,
so the alternate one (0.1% nominal) is unreachable on stock. This replaces
the branch that guards it with two `nop`s:

| address | stock | new |
|---|---|---|
| `0x4006c2fa` | `6f 00 00 d6` (`ble.w`) | `4e 71 4e 71` (`nop; nop`) |

It has **no sources**, so it builds without a cross toolchain. See
[../../docs/TECHNICAL.md](../../docs/TECHNICAL.md).

## Build and install

```sh
cd elekloader
python -m elekloader.sdk.build ../digitakt-splash-mods/mods/rare-splash --stock Digitakt_OS1.53.syx
python -m elekloader.patch --stock Digitakt_OS1.53.syx \
    --mod mods/core/out/core-2.1.elemod \
    --mod ../digitakt-splash-mods/mods/rare-splash/out/rare-splash-1.0.elemod \
    --out rare.syx --version 2.0c
```

`rare-splash`, `digitussy` and `digitrash` patch the same instruction or
site, so install only one of them.
