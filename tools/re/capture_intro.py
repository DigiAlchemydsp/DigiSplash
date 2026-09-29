#!/usr/bin/env python3
"""Capture the Digitakt mk1 intro animation, one PNG per frame.

Resumes a pre-intro snapshot and delivers PIT3 the way mk1 wants (the intro
PARKS on the frame semaphore, so the tick is the only thing that advances it).
Captures the panel framebuffer at every PIT3 tick, which is one completed
frame, and stops shortly after the intro's exit sequence (0x4006cb94).

    python capture_intro.py --syx F.syx --snapshot boot.snap --out out/frames
"""
import argparse
import hashlib
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _paths import find                                  # noqa: E402

sys.path.insert(0, find('DIGIEMU_DIR', 'digiemu-main',
                        '..', '../..', '../../..'))

from emu import config, longrun, panel, symbols          # noqa: E402
from emu.dtim import Dtims, Timers                        # noqa: E402
from emu.pit import Pits                                  # noqa: E402

W, H = 128, 64
PIT3_VECTOR_SLOT = 0x40000340
PIT3_BASE = 0xFC08C000
INTRO_ISR = 0x4006C154
INTRO_DONE = 0x4006CB94


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--syx', required=True)
    ap.add_argument('--snapshot', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--budget', type=lambda s: int(s, 0), default=200_000_000)
    ap.add_argument('--chunk', type=lambda s: int(s, 0), default=200_000)
    ap.add_argument('--limit', type=int, default=260)
    a = ap.parse_args()

    img = open(config.main_image(), 'rb').read()
    prof = symbols.resolve(img, load_addr=0x40000400)
    fb_front = prof.fb_front
    if fb_front is None:
        raise SystemExit('no fb_front symbol for this image')

    m, ev, st, pc, inq, at = longrun.build(
        a.snapshot, syx=a.syx, unblock=True, softfloat=True,
        bitmap=True, dsp=True, on_pixel=None)

    pit = Pits(m, channels=(3,), hold=False)
    dtim = Dtims(m, channels=(3,), hold=True)
    pits = Timers(pit, dtim)

    os.makedirs(a.out, exist_ok=True)
    state = {'frames': 0, 'done': 0, 'last': None}

    def on_tick(*_):
        if state['done']:
            return
        buf = panel.read(m, fb_front)
        if buf is None:
            return
        h = hashlib.sha1(bytes(buf)).hexdigest()
        if h == state['last']:
            return
        state['last'] = h
        state['frames'] += 1
        if state['frames'] > a.limit:
            return
        path = os.path.join(a.out, 'frame-%03d.png' % state['frames'])
        panel.write_png(buf, path, scale=4)
        print('  frame %3d  lit %-5d -> %s'
              % (state['frames'], len(panel.lit(buf)),
                 os.path.basename(path)), flush=True)

    def handover(*_):
        state['done'] += 1
        if state['done'] == 1:
            pit.channels = (3, 2, 0)
            pits.release()

    at(INTRO_ISR, on_tick)
    at(INTRO_DONE, handover)

    print('resume %s  vector=0x%08x PCSR=0x%04x'
          % (os.path.basename(a.snapshot),
             int.from_bytes(m.uc.mem_read(PIT3_VECTOR_SLOT, 4), 'big'),
             int.from_bytes(m.uc.mem_read(PIT3_BASE, 2), 'big')))

    total = 0
    while total < a.budget and state['frames'] <= a.limit:
        pc, executed, why = longrun.spin(m, pc, a.chunk, pits=pits)
        total += executed
        if state['done']:
            break
        if pc == 0:
            print('  stop: pc zero', flush=True)
            break
    print('captured %d frames in %d instructions' % (state['frames'], total))


if __name__ == '__main__':
    main()
