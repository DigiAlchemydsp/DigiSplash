# match

Generated from `tumblr_n8ggiogZGX1rmhormo1_1280.gif` (41 frames) by make-bootanim.

Build it with elekloader, then patch it with core-dn1:

```sh
cd elekloader
python -m elekloader.sdk.build <this dir> --stock <stock .syx>
python -m elekloader.patch --stock <stock .syx> \
    --mod mods/core-dn1/out/core-dn1-2.0a.elemod \
    --mod <this dir>/out/match-1.0.elemod --out out.syx --version 2.0x
```
