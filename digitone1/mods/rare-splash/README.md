# rare-splash (Digitone mk1 / Keys, OS 1.43)

Boots on the **alternate** stock splash animation. Needs `core` (core-dn1).

## How it works

The intro picks between two animations from a generator that is never seeded,
so the alternate one is unreachable on stock. This replaces the branch that
guards it with two `nop`s:

| address | stock | new |
|---|---|---|
| `0x40090e82` | `6f 00 01 a2` (`ble.w`) | `4e 71 4e 71` (`nop; nop`) |

It has **no sources**, so it builds without a cross toolchain.

## Build and install

```sh
cd elekloader
python -m elekloader.sdk.build ../digitakt-splash-mods/digitone1/mods/rare-splash \
    --stock Digitone_and_Digitone_Keys_OS1.43.syx
python -m elekloader.patch --stock Digitone_and_Digitone_Keys_OS1.43.syx \
    --mod mods/core-dn1/out/core-dn1-2.0a.elemod \
    --mod ../digitakt-splash-mods/digitone1/mods/rare-splash/out/rare-splash-1.0.elemod \
    --out rare-dn1.syx --version 2.0s
```

Install only one of `rare-splash`, `digitussy` and `digitrash` (they overlap).
