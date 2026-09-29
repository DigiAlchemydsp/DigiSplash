/* SPDX-License-Identifier: GPL-2.0-or-later
 * DigiTussy: at each of the intro's panel presents, draw our animation over
 * the frame the intro just composed, then run the stock present.
 *
 * The sites are the intro's own `jsr <present>` calls (0x400f8efa is the
 * delta present, 0x400f8e7c the full flush), so the stock present functions
 * are left intact -- digiemu still resolves panel_diff/fb_front and can
 * check the build. See render.c and mod.json.
 */
        .section .run, "ax"

        .globl  dt_diff
        .globl  dt_flush

dt_diff:
        jsr     dt_draw
        jmp     0x400f8efa

dt_flush:
        jsr     dt_draw
        jmp     0x400f8e7c
