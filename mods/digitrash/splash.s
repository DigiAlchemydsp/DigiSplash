/* SPDX-License-Identifier: GPL-2.0-or-later
 * DigiTrash: at each of the intro's panel presents, draw our animation over
 * the frame the intro just composed, then run the stock present.
 *
 * The sites are the intro's own `jsr <present>` calls (0x400e60e2 is the
 * delta present, 0x400e6064 the full flush), so the stock present functions
 * are left intact -- digiemu still resolves panel_diff/fb_front and can
 * check the build. See render.c and mod.json.
 */
        .section .run, "ax"

        .globl  dtr_diff
        .globl  dtr_flush

dtr_diff:
        jsr     dtr_draw
        jmp     0x400e60e2

dtr_flush:
        jsr     dtr_draw
        jmp     0x400e6064
