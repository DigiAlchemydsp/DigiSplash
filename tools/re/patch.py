#!/usr/bin/env python3
"""Probe the Digitakt mk1 OS 1.53 boot animation selector, and patch it.

Findings (addresses are runtime; the main OS loads at 0x40000400, so the file
offset in section_3_MAIN_OS.bin is addr - 0x40000400):

The intro task entry 0x4006c2ae draws the boot animation.  At 0x4006c2ea it
draws one pseudo-random number and chooses between two whole animations:

    0x4006c2ec  lea.l  0x40105910.l, a6
    0x4006c2f0  jsr    (a6)                 ; rand()
    0x4006c2f2  mvs.w  d0, d0
    0x4006c2f4  cmpi.l #$7fdf, d0           ; 32735
    0x4006c2fa  ble.w  0x4006c3d2           ; ~99.9% -> the usual animation
               <fall through>               ; ~0.1%  -> the alternate animation

0x40105910 is the same textbook ANSI-C LCG the Digitakt II uses:

    state = state * 0x41c64e6d + 0x3039      (mod 2^32)
    out   = (state >> 16) & 0x7fff

Its state lives at 0x406481e8 and is written from exactly two places: the
generator itself, and a setter at 0x4010595a that nothing calls.  So the
generator is never seeded, the draw is identical on every boot, and the
alternate animation is unreachable -- the identical bug to Digitakt II.

    python patch.py reveal  Digitakt_OS1.53.syx dt1-reveal.syx
    python patch.py rare    Digitakt_OS1.53.syx dt1-rare.syx
    python patch.py info    Digitakt_OS1.53.syx
"""
import argparse
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _paths import find                                  # noqa: E402

sys.path.insert(0, find('ELEKLOADER_DIR', 'elekloader',
                        '..', '../..', '../../..'))
from elekloader import syx, devices                      # noqa: E402

LOAD = 0x40000400
STATE = 0x406481e8
RNG = 0x40105910
SEL_CMPI = 0x4006c2f4          # cmpi.l #$7fdf,d0
SEL_BRANCH = 0x4006c2fa        # ble.w 0x4006c3d2
RNG_ADD = 0x40105920           # addi.l #$3039,d0

THRESHOLD_FROM = b'\x00\x00\x7f\xdf'
THRESHOLD_TO = b'\x00\x00\x3f\xff'          # 50 / 50
BRANCH_FROM = b'\x6f\x00\x00\xd6'           # ble.w 0x4006c3d2
BRANCH_NOP = b'\x4e\x71\x4e\x71'            # nop ; nop -> always alternate
RNG_ADD_FROM = b'\x06\x80\x00\x00\x30\x39'  # addi.l #12345,d0
RNG_ADD_TO = b'\xd0\xb9\xfc\x07\x00\x0c'    # add.l 0xFC07000C,d0 (DMA timer 0)


def image(syx_bytes):
    s = syx.Syx.load(syx_bytes) if isinstance(syx_bytes, str) else syx_bytes
    return s, s.section(3)


def file_off(addr):
    return addr - LOAD


def ensure(img, addr, want):
    o = file_off(addr)
    got = img[o:o + len(want)]
    if got != want:
        raise SystemExit('0x%08x holds %s, expected %s'
                         % (addr, got.hex(), want.hex()))


def apply_patch(img, addr, frm, to):
    ensure(img, addr, frm)
    o = file_off(addr)
    img[o:o + len(to)] = to
    print('  patch 0x%08x  %s -> %s' % (addr, frm.hex(), to.hex()))


def make(src, dst, kind):
    stock = syx.Syx.load(src)
    img = bytearray(stock.section(3))
    print('%s -> %s   (%s)' % (os.path.basename(src), os.path.basename(dst), kind))
    if kind in ('reveal', 'equalize'):
        apply_patch(img, SEL_CMPI + 2, THRESHOLD_FROM, THRESHOLD_TO)
    if kind in ('reveal', 'entropy'):
        apply_patch(img, RNG_ADD, RNG_ADD_FROM, RNG_ADD_TO)
    if kind in ('rare', 'force-alternate'):
        apply_patch(img, SEL_BRANCH, BRANCH_FROM, BRANCH_NOP)

    dev = [d for d in devices._all() if d.key == 'digitakt-mk1'][0]
    out = syx.write(stock, syx.pack_main(img), dev)
    open(dst, 'wb').write(out)
    facts = syx.verify(out, stock, img, dev)
    print('  wrote %s (%d bytes)' % (dst, len(out)))
    print('  verify: main %d bytes, inplace_min_gap %d, %s'
          % (facts['main']['image'], facts['main']['inplace_min_gap'],
             facts['sha256'][:16]))


def info(src):
    stock = syx.Syx.load(src)
    img = stock.section(3)
    print('syx      %s' % src)
    print('version  %s' % stock.version)
    print('main OS  %d bytes at 0x%08x' % (len(img), LOAD))
    print('selector 0x%08x  cmpi.l #0x%x -> %s'
          % (SEL_CMPI, struct.unpack_from('>I', img, file_off(SEL_CMPI) + 2)[0],
             'alternate when > 0x7fdf (0.1%)'))
    print('rng      0x%08x  addi.l #0x%x  (state 0x%08x, never seeded)'
          % (RNG_ADD, struct.unpack_from('>I', img, file_off(RNG_ADD) + 2)[0], STATE))


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('kind', choices=['reveal', 'equalize', 'entropy',
                                     'rare', 'force-alternate', 'info'])
    ap.add_argument('src')
    ap.add_argument('dst', nargs='?')
    a = ap.parse_args()
    if a.kind == 'info':
        info(a.src)
        return
    if not a.dst:
        raise SystemExit('%s needs an output .syx' % a.kind)
    make(a.src, a.dst, a.kind)


if __name__ == '__main__':
    main()
