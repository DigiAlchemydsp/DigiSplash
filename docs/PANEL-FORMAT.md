# Panel format and making your own art

The Digitakt mk1 panel is **128 × 64, 1 bit per pixel**. A frame is 1024
bytes laid out like an SSD1306 page framebuffer, except the **page order is
inverted** (a remapped COM scan direction):

```
byte index = page + 8 * column          page 0..7, column 0..127
bit n of that byte = row 8 * (7 - page) + n     (n = 0 is that page's top row)
```

So pixel `(x, y)` with `y = 0` at the **top** is:

```c
buf[(7 - (y >> 3)) + (x << 3)] |= 1u << (y & 7);   /* set */
buf[(7 - (y >> 3)) + (x << 3)] &= ~(1u << (y & 7)); /* clear */
```

`x` runs left→right (columns are **not** reversed); `y` runs top→bottom.

## PNG → panel bytes

`mods/custom-splash/mksplash.py` does the conversion:

```sh
python mksplash.py logo.png splash.bin
python mksplash.py --text "HELLO" splash.bin          # no input file
python mksplash.py logo.png splash.bin --dither       # Floyd–Steinberg
python mksplash.py logo.png splash.bin --invert       # swap ink and paper
python mksplash.py logo.png splash.s --asm            # .byte block instead
```

It fits the image to 128×64 preserving aspect, thresholds at 128 (or dithers),
packs the bytes, and prints an ASCII preview. It needs Pillow
(`pip install pillow`).

Design notes:

- The panel **lights the 1 bits**, so a normal black-on-white logo should be
  converted as-is; invert only if your source is white-on-black.
- Avoid 1-pixel detail — it dithers into noise. Bold shapes and 5×7-ish text
  read best.
- `--asm` output is handy when you want the bytes as a `.byte` block inside a
  source file rather than an `.incbin`ed `splash.bin`.

## Drawing from code

The C mods here (`digitussy`, `digitrash`) draw directly with:

```c
static u8 *fb = (u8 *) * (volatile u32 *)0x4020d8f8;   /* the front buffer */
static void px(i32 x, i32 y) {
    if (y < 0 || x < 0 || x > 127 || y > 63) return;
    fb[(7 - (y >> 3)) + (x << 3)] |= (u8)(1u << (y & 7));
}
```

They also carry a 5×7 font (column-major, bit 0 = top row) and a small LCG
for motion. `docs/TECHNICAL.md` explains when `0x4020d8f8` holds what the
panel shows.
