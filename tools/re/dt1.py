#!/usr/bin/env python3
"""Static-analysis helper for the Digitakt mk1 OS 1.53 main OS image.

Image loads at 0x40000400. Usage:

    python dt1.py disas 0x400d3fb6 --count 60
    python dt1.py disas 0x400d3ab6 --until 0x400d3e94
    python dt1.py hex 0x4028ae2c --len 256
    python dt1.py word 0x4028ae2c 16
    python dt1.py render 0x4028ae98 out.png
"""
import argparse
import os
import struct
import sys
import zlib

from capstone import Cs, CS_ARCH_M68K, CS_MODE_BIG_ENDIAN, CS_MODE_M68K_040

HERE = os.path.dirname(os.path.abspath(__file__))
IMG_PATH = os.environ.get('DT1_IMG') or os.path.join(HERE, 'section_3_MAIN_OS.bin')
LOAD = 0x40000400

_md = Cs(CS_ARCH_M68K, CS_MODE_BIG_ENDIAN | CS_MODE_M68K_040)
_md.detail = False


def img():
    return open(IMG_PATH, 'rb').read()


def off(addr):
    return addr - LOAD


def read(addr, n):
    d = img()
    return d[off(addr):off(addr) + n]


def decode_mvsz(d, o):
    if o + 2 > len(d):
        return None
    w = struct.unpack_from('>H', d, o)[0]
    if (w & 0xF100) != 0x7100:
        return None
    dn, ss, mmm, rrr = (w >> 9) & 7, (w >> 6) & 3, (w >> 3) & 7, w & 7
    mn = {0: 'mvs.b', 1: 'mvs.w', 2: 'mvz.b', 3: 'mvz.w'}[ss]
    if mmm == 7 and rrr == 1:
        return mn, '$%08x.l, d%d' % (struct.unpack_from('>I', d, o + 2)[0], dn), 6
    if mmm == 7 and rrr == 0:
        return mn, '$%04x.w, d%d' % (struct.unpack_from('>H', d, o + 2)[0], dn), 4
    if mmm == 5:
        d16 = struct.unpack_from('>h', d, o + 2)[0]
        return mn, '%s$%x(a%d), d%d' % ('-' if d16 < 0 else '', abs(d16), rrr, dn), 4
    if mmm == 6:
        ext = struct.unpack_from('>H', d, o + 2)[0]
        xn = (ext >> 12) & 0xF
        xreg = ('a%d' % (xn - 8)) if xn >= 8 else ('d%d' % xn)
        wl = 'l' if ext & 0x0800 else 'w'
        disp = ext & 0xFF
        return mn, '$%x(a%d, %s.%s), d%d' % (disp, rrr, xreg, wl, dn), 4
    simple = {0: 'd%d, d%%d' % rrr, 2: '(a%d), d%%d' % rrr,
              3: '(a%d)+, d%%d' % rrr, 4: '-(a%d), d%%d' % rrr}
    if mmm in simple:
        return mn, simple[mmm] % dn, 2
    return None


def decode_ff1(d, o):
    w = struct.unpack_from('>H', d, o)[0]
    if 0x04C0 <= w <= 0x04C7:
        return 'ff1.l', 'd%d' % (w & 7), 2
    return None


def disasm(d, start, end):
    pc = start
    while pc < end:
        o = off(pc)
        hit = decode_mvsz(d, o) or decode_ff1(d, o)
        if hit:
            mn, ops, sz = hit
            yield pc, d[o:o + sz].hex(), mn, ops
            pc += sz
            continue
        produced = False
        for ins in _md.disasm(d[o:off(end)], pc):
            nxt = off(ins.address)
            if ins.address > pc and (decode_mvsz(d, nxt) or decode_ff1(d, nxt)):
                break
            yield ins.address, ins.bytes.hex(), ins.mnemonic, ins.op_str
            pc = ins.address + ins.size
            produced = True
            if pc >= end:
                break
            o2 = off(pc)
            if decode_mvsz(d, o2) or decode_ff1(d, o2):
                break
        if not produced:
            w = struct.unpack_from('>H', d, off(pc))[0]
            yield pc, '%04x' % w, '.word', '$%04x' % w
            pc += 2


def annotate(val):
    o = off(val)
    if val >= LOAD and 0 <= o < len(img()):
        d = img()
        e = d.find(b'\x00', o)
        if 0 < e - o < 48:
            t = d[o:e]
            if sum(1 for c in t if 32 <= c < 127) >= 4:
                return '  ; %r' % t.decode('latin1')
    return ''


def cmd_disas(a):
    d = img()
    if a.until:
        end = a.until
    else:
        end = a.addr + a.count * 10
    for addr, hx, mn, ops in disasm(d, a.addr, end):
        note = annotate_tokens(ops) if a.notes else ''
        print('0x%08x  %-22s %-8s %-34s%s' % (addr, hx, mn, ops, note))


def annotate_tokens(ops):
    out = []
    for tok in ops.replace('(', ' ').replace(')', ' ').replace(',', ' ').split():
        tok = tok.strip('#$')
        if not tok:
            continue
        try:
            val = int(tok, 16)
        except ValueError:
            continue
        if val >= LOAD:
            s = annotate(val)
            if s:
                out.append(s.strip())
                break
    return ('  ; ' + ' | '.join(out)) if out else ''


def cmd_hex(a):
    d = read(a.addr, a.len)
    base = off(a.addr)
    for i in range(0, len(d), 16):
        chunk = d[i:i + 16]
        hx = ' '.join('%02x' % b for b in chunk)
        asc = ''.join(chr(b) if 32 <= b < 127 else '.' for b in chunk)
        print('%08x  %-47s  %s' % (base + i, hx, asc))


def cmd_word(a):
    d = img()
    for i in range(a.n):
        o = off(a.addr) + i * 4
        v = struct.unpack_from('>I', d, o)[0]
        print('%08x  %08x  %d' % (LOAD + o, v, v if v < 0x80000000 else v - 0x100000000))


def png(pixels, w, h):
    raw = b''.join(b'\x00' + bytes(pixels[y * w:(y + 1) * w]) for y in range(h))
    def chunk(tag, data):
        c = tag + data
        return struct.pack('>I', len(data)) + c + struct.pack('>I', zlib.crc32(c))
    return (b'\x89PNG\r\n\x1a\n'
            + chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 0, 0, 0, 0))
            + chunk(b'IDAT', zlib.compress(raw, 9))
            + chunk(b'IEND', b''))


def cmd_render(a):
    d = img()
    pd = a.addr
    w, h, buf = struct.unpack_from('>III', d, off(pd))
    print('PixelData @0x%08x  %dx%d  buffer=0x%08x' % (pd, w, h, buf))
    if w > 4096 or h > 4096:
        print('implausible dimensions; not rendering')
        return
    src = d[off(buf):off(buf) + w * h]
    out = bytearray(w * h)
    for i, v in enumerate(src):
        out[i] = 255 if v > 0x80 else 0
    open(a.out, 'wb').write(png(out, w, h))
    print('wrote', a.out)
    if w <= 140:
        for y in range(h):
            print(''.join('#' if out[y * w + x] else '.' for x in range(w)))


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest='cmd', required=True)
    p = sub.add_parser('disas')
    p.add_argument('addr', type=lambda s: int(s, 0))
    p.add_argument('--count', type=int, default=40)
    p.add_argument('--until', type=lambda s: int(s, 0), default=0)
    p.add_argument('--notes', action='store_true')
    p.set_defaults(func=cmd_disas)
    p = sub.add_parser('hex')
    p.add_argument('addr', type=lambda s: int(s, 0))
    p.add_argument('--len', type=int, default=64)
    p.set_defaults(func=cmd_hex)
    p = sub.add_parser('word')
    p.add_argument('addr', type=lambda s: int(s, 0))
    p.add_argument('n', type=int, nargs='?', default=8)
    p.set_defaults(func=cmd_word)
    p = sub.add_parser('render')
    p.add_argument('addr', type=lambda s: int(s, 0))
    p.add_argument('out')
    p.set_defaults(func=cmd_render)
    a = ap.parse_args()
    a.func(a)


if __name__ == '__main__':
    main()
