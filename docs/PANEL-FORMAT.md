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

[`tools/make-bootanim`](../tools/make-bootanim) is the converter: it fits the
image (or every GIF frame) to 128×64, thresholds at 128 or dithers, packs each
frame, and writes the mod's `frames.bin` (the raw panel bytes, one 1024-byte
frame after another).

```sh
tools\make-bootanim\make-bootanim.bat logo.png
tools\make-bootanim\make-bootanim.bat anim.gif --frames 40
tools\make-bootanim\make-bootanim.bat logo.png --invert --dither
```

It needs Python 3 with Pillow (`pip install pillow`). The `frames.bin` it
writes is exactly the bytes a mod copies to the panel, so a hand-written mod
can `.incbin` it too.

Design notes:

- The panel **lights the 1 bits**, so a normal black-on-white logo should be
  converted as-is; invert only if your source is white-on-black.
- Avoid 1-pixel detail — it dithers into noise. Bold shapes and 5×7-ish text
  read best.

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
