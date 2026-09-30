# releases

Prebuilt boot-splash mods — **only `.elemod` files**, one per splash, in both
device variants:

- `dt/` — Digitakt mk1, OS 1.53 (needs `core`, e.g. `core-2.1.elemod`)
- `dn/` — Digitone mk1 / Keys, OS 1.43 (needs `core-dn1`, e.g.
  `core-dn1-2.0a.elemod`)

Each device is also packaged as a zip:

- `DigiSplash-1.1-<device>.zip` — the twelve splashes below, **elemods only**
  (`elemods/` + README + LICENSE).
- `DigiSplash-1.0-<device>.zip` — the earlier full package, with sources
  (`elemods/` + `sources/` + README + LICENSE).

| mod | what |
|---|---|
| `rare-splash` | the alternate stock boot animation, the one the unseeded selector never reaches |
| `digitussy` | animated wordmark + rising particles |
| `digitrash` | animated wordmark, trash can and six flies |
| `aba-bootanim` | the `aba.gif` example animation |
| `loox` | animated GIF (`1_CqtKSeLhUEUfiXsnYMqfbQ`), 35 frames |
| `tussy` | animated GIF (`Primp`), 59 frames |
| `bzme` | the animated GIF `bzme.gif`, 14 frames |
| `reach` | animated GIF (`0efb8c5f…`), 18 frames |
| `claw` | animated GIF (`b6906df9…`), 18 frames |
| `tidemoon` | animated GIF (`Qd87v2`), 60 frames |
| `vinyl` | animated GIF (`tumblr_1edd57ba…`), 24 frames |
| `match` | animated GIF (`tumblr_n8ggiog…`), 41 frames |

Every mod except `rare-splash` is a **draw mod** and animates;
`rare-splash` switches which stock animation runs.

A screenshot of each (in [`screenshots/`](screenshots)); `reach`, `claw`,
`tidemoon`, `vinyl` and `match` are captured from the emulator (digiemu), one
full animation cycle each:

![rare-splash](screenshots/rare-splash.gif)
![digitussy](screenshots/digitussy.gif)
![digitrash](screenshots/digitrash.gif)
![aba](screenshots/aba-bootanim.gif)
![loox](screenshots/loox.gif)
![tussy](screenshots/tussy.gif)
![bzme](screenshots/bzme.gif)
![reach](screenshots/reach.gif)
![claw](screenshots/claw.gif)
![tidemoon](screenshots/tidemoon.gif)
![vinyl](screenshots/vinyl.gif)
![match](screenshots/match.gif)

## Install

With elekloader:

```sh
python -m elekloader.patch --stock Digitakt_OS1.53.syx \
    --mod mods/core/out/core-2.1.elemod \
    --mod releases/dt/digitussy.elemod --out digitussy.syx --version 2.0x

python -m elekloader.patch --stock Digitone_and_Digitone_Keys_OS1.43.syx \
    --mod mods/core-dn1/out/core-dn1-2.0a.elemod \
    --mod releases/dn/digitussy.elemod --out digitussy-dn.syx --version 2.0x
```

Or drop the `.elemod` into the loader window (Install from file) together with
the matching core.

## Conflict

Every mod here except `rare-splash` is a **draw mod**: they hook the same
intro present call sites, so install **one** of them. `rare-splash` patches a
different instruction and can be combined, but a draw mod paints the whole
frame, so `rare-splash` is then invisible — install it alone to see the
alternate stock animation.

## Notes

- These `.elemod` files contain the mod's own bytes (including the packed
  frames); no Elektron firmware. See [../NOTICE.md](../NOTICE.md).
- Rebuild any of them with `elekloader.sdk.build` from the sources under
  `../mods`, `../digitone1/mods`, or regenerate a bootanim with
  [`../tools/make-bootanim`](../tools/make-bootanim).

## DigiScreen overlays

This `releases/` tree is **boot animations only**. The **DigiScreen** overlay
mods — which toggle a full-panel image over the *live UI* with `TRK`+`YES`
(Digitakt) / `MIDI`+`YES` (Digitone), press again to remove — are not shipped
here. They live in the DigiScreen project's own releases:

- `../DigiScreen/releases/<name>-dt.elemod` (Digitakt mk1)
- `../DigiScreen/releases/<name>-dn.elemod` (Digitone mk1 / Keys)

built from the same animations (`loox`, `tussy`, `bzme`, `reach`, `claw`,
`tidemoon`, …) with `../DigiScreen/tools/make_machine.py`.
