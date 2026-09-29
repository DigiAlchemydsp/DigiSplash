#!/usr/bin/env python3
"""Convert a 128x64 image into the Digitakt mk1 panel format.

The panel is 128x64, 1 bit per pixel, stored like an SSD1306 page framebuffer
but with the page order inverted (see digiemu emu/panel.py):

    byte index = page + 8 * column     page 0..7, column 0..127
    bit n of that byte = row 8 * (7 - page) + n     (n = 0 is the top of a page)

This reads any image Pillow can open, fits it to 128x64, and writes the raw
1024-byte image a splash mod .incbin's. `--asm` writes a GNU as `.byte` block
instead, `--text` renders text with Pillow's built-in font (no input image).

    python mksplash.py logo.png splash.bin
    python mksplash.py --text "CUSTOM" splash.bin
    python mksplash.py logo.png splash.bin --dither --invert
"""
import argparse
import sys

W, H = 128, 64
PANEL_BYTES = W * H // 8


def pack(img):
    """A Pillow '1' image -> the panel's 1024 bytes."""
    if img.size != (W, H):
        img = img.resize((W, H))
    px = img.convert('1').load()
    buf = bytearray(PANEL_BYTES)
    for y in range(H):
        page = 7 - (y // 8)
        bit = y % 8
        base = page
        for x in range(W):
            if px[x, y]:
                buf[base + 8 * x] |= 1 << bit
    return bytes(buf)


def fit(img):
    """Scale to fit 128x64, preserving aspect, centred on a black canvas."""
    from PIL import Image
    img = img.convert('L')
    scale = min(W / img.width, H / img.height)
    nw, nh = max(1, round(img.width * scale)), max(1, round(img.height * scale))
    img = img.resize((nw, nh))
    canvas = Image.new('L', (W, H), 0)
    canvas.paste(img, ((W - nw) // 2, (H - nh) // 2))
    return canvas


def from_text(text):
    """Render `text` with Pillow's built-in font, scaled up to be readable."""
    from PIL import Image, ImageDraw
    tmp = Image.new('L', (1, 1))
    d = ImageDraw.Draw(tmp)
    box = d.textbbox((0, 0), text)
    tw, th = box[2] - box[0], box[3] - box[1]
    src = Image.new('L', (max(1, tw), max(1, th)), 0)
    ImageDraw.Draw(src).text((-box[0], -box[1]), text, fill=255)
    scale = max(1, min(W // max(1, tw), H // max(1, th)))
    src = src.resize((tw * scale, th * scale))
    canvas = Image.new('L', (W, H), 0)
    canvas.paste(src, ((W - src.width) // 2, (H - src.height) // 2))
    return canvas


def to_asm(data):
    lines = ['        .balign 2', 'csp_image:']
    for i in range(0, len(data), 16):
        chunk = data[i:i + 16]
        lines.append('        .byte ' + ', '.join('0x%02x' % b for b in chunk))
    return '\n'.join(lines) + '\n'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('input', nargs='?', help='a PNG/JPG/... (omit with --text)')
    ap.add_argument('out', help='the .bin to write (or .s with --asm)')
    ap.add_argument('--text', help='render this text instead of an image')
    ap.add_argument('--invert', action='store_true',
                    help='swap black and white (the panel lights the 1 bits)')
    ap.add_argument('--dither', action='store_true',
                    help='Floyd-Steinberg dither instead of a hard threshold')
    ap.add_argument('--asm', action='store_true',
                    help='write a GNU as .byte block instead of a .bin')
    a = ap.parse_args()

    if a.text:
        img = from_text(a.text)
    elif a.input:
        from PIL import Image
        img = fit(Image.open(a.input))
    else:
        ap.error('give an input image or --text')

    if a.text:
        img = img  # already a black canvas with white glyphs
    if a.invert:
        img = img.point(lambda v: 255 - v)
    if a.dither:
        one = img.convert('1')                   # Pillow dithers by default
    else:
        one = img.point(lambda v: 255 if v > 127 else 0).convert('1')

    data = pack(one)
    if a.asm:
        open(a.out, 'w').write(to_asm(data))
    else:
        open(a.out, 'wb').write(data)
    print('wrote %s (%d bytes) from %s'
          % (a.out, len(data), a.text or a.input))
    # a quick terminal preview
    for y in range(H):
        print('  ' + ''.join('#' if data[(7 - (y // 8)) + 8 * x] >> (y % 8) & 1
                             else '.' for x in range(W)))


if __name__ == '__main__':
    sys.exit(main())
