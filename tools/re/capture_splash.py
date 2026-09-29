#!/usr/bin/env python3
"""Capture the splash the panel is shown, one PNG per present.

Resumes a pre-intro snapshot, delivers PIT3 the mk1 way, and grabs the frame
at the stock present body (0x400e60ea for the diff, 0x400e606c for the full
flush) -- after any splash mod has drawn over the front buffer. Reads
[0x4020d8f8], the buffer just composed.

    python capture_splash.py --syx F.syx --snapshot boot.snap --out frames
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

PIT3_VECTOR_SLOT = 0x40000340
INTRO_DONE = 0x4006CB94
DIFF_BODY = 0x400e60ea
FLUSH_BODY = 0x400e606c


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--syx', required=True)
    ap.add_argument('--snapshot', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--budget', type=lambda s: int(s, 0), default=120_000_000)
    ap.add_argument('--chunk', type=lambda s: int(s, 0), default=20_000_000)
    ap.add_argument('--limit', type=int, default=120)
    ap.add_argument('--fb-front', type=lambda s: int(s, 0), default=0x4020d8f8)
    ap.add_argument('--diff-body', type=lambda s: int(s, 0), default=0x400e60ea)
    ap.add_argument('--flush-body', type=lambda s: int(s, 0), default=0x400e606c)
    ap.add_argument('--intro-done', type=lambda s: int(s, 0), default=0x4006CB94)
    a = ap.parse_args()

    m, ev, st, pc, inq, at = longrun.build(
        a.snapshot, syx=a.syx, unblock=True, softfloat=True,
        bitmap=True, dsp=True)
    pit = Pits(m, channels=(3,), hold=False)
    dtim = Dtims(m, channels=(3,), hold=True)
    pits = Timers(pit, dtim)

    os.makedirs(a.out, exist_ok=True)
    state = {'frames': 0, 'done': 0, 'last': None}

    def grab(*_):
        if state['frames'] >= a.limit:
            return
        try:
            buf = panel.read(m, a.fb_front)
        except Exception:
            buf = None
        if not buf:
            return
        h = hashlib.sha1(bytes(buf)).hexdigest()
        if h == state['last']:
            return
        state['last'] = h
        state['frames'] += 1
        path = os.path.join(a.out, 'frame-%03d.png' % state['frames'])
        panel.write_png(buf, path, scale=4)
        print('  frame %3d  lit %-5d -> %s'
              % (state['frames'], len(panel.lit(buf)), os.path.basename(path)),
              flush=True)

    def handover(*_):
        state['done'] += 1
        if state['done'] == 1:
            pit.channels = (3, 2, 0)
            pits.release()

    at(a.diff_body, grab)
    at(a.flush_body, grab)
    at(a.intro_done, handover)

    print('resume %s' % os.path.basename(a.snapshot))
    total = 0
    while total < a.budget and state['done'] == 0:
        pc, executed, why = longrun.spin(m, pc, a.chunk, pits=pits)
        total += executed
        if pc == 0:
            print('  stop: pc zero')
            break
    print('captured %d distinct frames in %d instructions'
          % (state['frames'], total))


if __name__ == '__main__':
    main()
