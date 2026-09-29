#!/usr/bin/env python3
"""Capture the intro animation straight from the cold boot.

Most of the 180 intro frames are drawn while the firmware comes up, before it
parks (the ladder does not deliver PIT3, but the draw task still runs). So
this drives emu.dspboot.run's machine itself under the native block budget,
exactly like emu.bootstrap.cold_boot, and snapshots the panel framebuffer
whenever it changes. That catches the whole animation, not just the tail a
boot.snap holds.

    python cold_capture.py --syx F.syx --out frames --limit 170000000
"""
import argparse
import hashlib
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _paths import find                                  # noqa: E402

sys.path.insert(0, find('DIGIEMU_DIR', 'digiemu-main',
                        '..', '../..', '../../..'))

from emu import config, dspboot, native, panel, symbols      # noqa: E402
from emu.harness import UC_M68K_REG_PC                        # noqa: E402
from emu.longrun import _FastStepper                          # noqa: E402


PIT3_SLOT = 0x40000340
POST_ISR = 0x400E5CEC


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--syx', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--limit', type=lambda s: int(s, 0), default=170_000_000)
    ap.add_argument('--chunk', type=lambda s: int(s, 0), default=250_000)
    ap.add_argument('--maxframes', type=int, default=400)
    ap.add_argument('--fb-front', type=lambda s: int(s, 0), default=0,
                    help='override the fb_front pointer global (mk1 1.53: 0x4020d8f8)')
    a = ap.parse_args()

    img = open(config.main_image(), 'rb').read()
    prof = symbols.resolve(img, load_addr=0x40000400)
    fbf = a.fb_front or prof.fb_front
    if fbf is None:
        fbf = 0x4020d8f8          # Digitakt mk1 1.53
    print('fb_front pointer global = 0x%08x' % fbf)

    box = {}
    m, st, _ = dspboot.run(a.syx, img, limit=None, fast=True, coverage=False,
                           machine_out=box, sdgate=True, esdhc=True)
    pc = box['start_pc']
    budget = native.NativeBudget(m.uc) if native.budget_available(m.uc) else None
    blocks = max(1, int(a.chunk / _FastStepper.PER_BLOCK))

    os.makedirs(a.out, exist_ok=True)
    done = 0
    last = None
    frames = 0
    intro_done = False
    while done < a.limit:
        m.halt_vec = None
        if budget is not None:
            budget.state.left = blocks
            m.uc.emu_start(pc, 0)
        else:
            m.uc.emu_start(pc, 0, count=a.chunk)
        pc = m.uc.reg_read(UC_M68K_REG_PC)
        done += a.chunk
        if m.halt_vec is not None:
            print('unhandled vector %s at ~%dM' % (m.halt_vec, done // 1_000_000))
            break
        try:
            buf = panel.read(m, fbf)
        except Exception:
            buf = None
        if buf:
            h = hashlib.sha1(bytes(buf)).hexdigest()
            if h != last:
                last = h
                frames += 1
                if frames <= a.maxframes:
                    panel.write_png(buf, os.path.join(
                        a.out, 'frame-%03d.png' % frames), scale=4)
                    print('  frame %3d  lit %-5d  ~%dM'
                          % (frames, len(panel.lit(buf)), done // 1_000_000),
                          flush=True)
        slot = int.from_bytes(m.uc.mem_read(PIT3_SLOT, 4), 'big')
        if slot == POST_ISR and not intro_done:
            intro_done = True
            print('  intro handed over at ~%dM' % (done // 1_000_000))
            break

    print('captured %d distinct frames in ~%dM instructions (native=%s)'
          % (frames, done // 1_000_000, budget is not None))


if __name__ == '__main__':
    main()
