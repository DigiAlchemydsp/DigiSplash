/* SPDX-License-Identifier: GPL-2.0-or-later
 * Custom splash: at each of the intro's panel presents, copy splash.bin (a
 * 1024-byte panel image) over the frame the intro just composed, then run
 * the stock present.
 *
 * The sites are the intro's own `jsr <present>` calls, so the stock present
 * functions are left intact -- digiemu still resolves panel_diff/fb_front
 * and can check the build. The image is 128x64, 1bpp, byte = page + 8*column,
 * page = 7 - (y>>3), bit = y&7; make one with mksplash.py.
 */
        .section .run, "ax"

        .globl  csp_diff
        .globl  csp_flush

csp_diff:
        bsr     csp_overlay
        jmp     0x400f8efa

csp_flush:
        bsr     csp_overlay
        jmp     0x400f8e7c

/* Copy csp_image over the front buffer while the intro still owns PIT3. */
csp_overlay:
        move.l  0x40000340,%d0          /* PIT3 vector slot */
        cmpi.l  #0x40090cdc,%d0         /* the intro's handler? */
        bne.s   1f
        move.l  0x40241a44,%a0          /* fb_front: the buffer about to show */
        tst.l   %a0
        beq.s   1f
        move.l  #csp_image,%a1
        move.l  #256,%d0
0:      move.l  (%a1)+,(%a0)+
        subq.l  #1,%d0
        bne.s   0b
1:      rts

        .balign 2
csp_image:
        .incbin "splash.bin"
