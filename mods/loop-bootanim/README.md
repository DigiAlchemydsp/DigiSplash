# loop

Generated from `c8aabc535054f1a1317881fb53540698.gif` (40 frames) by make-bootanim.

Build it with elekloader, then patch it with core:

```sh
cd elekloader
python -m elekloader.sdk.build <this dir> --stock <stock .syx>
python -m elekloader.patch --stock <stock .syx> \
    --mod mods/core/out/core-2.1.elemod \
    --mod <this dir>/out/loop-1.0.elemod --out out.syx --version 2.0x
```
