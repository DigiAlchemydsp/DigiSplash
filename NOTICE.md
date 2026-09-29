# Notice

This project is **independent and is not affiliated with or endorsed by
Elektron**. Digitakt and Elektron are trademarks of their respective owners.

## No firmware

No Elektron firmware is included, and none should ever be committed. The mods
contain only their own bytes and hashes of stock bytes; they are applied to a
`Digitakt_OS1.53.syx` that you obtain yourself. The `.gitignore` excludes
firmware and anything derived from it (`*.syx`, `*.snap`, images, cards).

## Licence

The mods' own code and the tools here are **GPL-2.0-or-later** (see
[LICENSE](LICENSE)). That matches elekloader, which they are built for.

## Screenshots

- `screenshots/digitussy.gif`, `digitrash.gif` show
  **this project's own graphics**, rendered by the firmware in the emulator.
- `screenshots/usual-vs-rare.png`, `usual-splash.gif` and `rare-splash.gif`
  are captures of the **device's own** boot animation (the one in stock OS
  1.53). They are included for reference only, to document what `rare-splash`
  changes; they are Elektron's artwork, not this project's, and are not
  covered by the GPL above.

## Credit

Container-format and patching knowledge derives from `mischa85/elektron-firmware-tool`
(MIT), **elekloader**, and the **digiemu**/digikit reverse-engineering work.
