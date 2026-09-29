/* SPDX-License-Identifier: GPL-2.0-or-later
 * DigiTrash: the DIGITRASH wordmark and a trash can, six flies buzzing round.
 *
 * Called once per panel present while the intro owns PIT3. The panel is
 * 128x64, 1bpp, byte = page + 8*column, page = 7 - (y>>3), bit = y&7.
 */
typedef unsigned char u8;
typedef unsigned int u32;
typedef int i32;

#define FBP      (*(volatile u32 *)0x40241a44)
#define PIT3_VEC (*(volatile u32 *)0x40000340)
#define INTRO_ISR ((u32)0x40090cdc)

static u8 *fb;

static const u8 font[26][5] = {
    {0x7e,0x11,0x11,0x11,0x7e}, {0x7f,0x49,0x49,0x49,0x36},
    {0x3e,0x41,0x41,0x41,0x22}, {0x7f,0x41,0x41,0x22,0x1c},
    {0x7f,0x49,0x49,0x49,0x41}, {0x7f,0x09,0x09,0x01,0x01},
    {0x3e,0x41,0x49,0x49,0x7a}, {0x7f,0x08,0x08,0x08,0x7f},
    {0x00,0x41,0x7f,0x41,0x00}, {0x20,0x40,0x41,0x3f,0x01},
    {0x7f,0x08,0x14,0x22,0x41}, {0x7f,0x40,0x40,0x40,0x40},
    {0x7f,0x02,0x0c,0x02,0x7f}, {0x7f,0x04,0x08,0x10,0x7f},
    {0x3e,0x41,0x41,0x41,0x3e}, {0x7f,0x09,0x09,0x09,0x06},
    {0x3e,0x41,0x51,0x21,0x5e}, {0x7f,0x09,0x19,0x29,0x46},
    {0x46,0x49,0x49,0x49,0x31}, {0x01,0x01,0x7f,0x01,0x01},
    {0x3f,0x40,0x40,0x40,0x3f}, {0x1f,0x20,0x40,0x20,0x1f},
    {0x7f,0x20,0x18,0x20,0x7f}, {0x63,0x14,0x08,0x14,0x63},
    {0x07,0x08,0x70,0x08,0x07}, {0x61,0x51,0x49,0x45,0x43},
};

static u32 rs = 0x1a2b3c4du;
static u32 rnd(void) { rs = rs * 1103515245u + 12345u; return (rs >> 16) & 0x7fffu; }

static void px(i32 x, i32 y)
{
    if (y < 0 || x < 0 || x > 127 || y > 63) return;
    fb[(7 - (y >> 3)) + (x << 3)] |= (u8)(1u << (y & 7));
}

static void hline(i32 x0, i32 x1, i32 y) { for (; x0 <= x1; x0++) px(x0, y); }
static void vline(i32 x, i32 y0, i32 y1) { for (; y0 <= y1; y0++) px(x, y0); }

static void ch(i32 x, i32 y, char c)
{
    const u8 *g;
    i32 col, row;
    if (c >= 'a' && c <= 'z') c -= 32;
    if (c < 'A' || c > 'Z') return;
    g = font[c - 'A'];
    for (col = 0; col < 5; col++) {
        u8 b = g[col];
        for (row = 0; row < 7; row++)
            if (b & (1u << row)) px(x + col, y + row);
    }
}

static void word(i32 x, i32 y, const char *s)
{
    for (; *s; s++, x += 6) ch(x, y, *s);
}

static void can(i32 x, i32 y)
{
    hline(x + 5, x + 10, y);          /* handle */
    hline(x, x + 15, y + 2);          /* lid */
    vline(x + 1, y + 4, y + 18);      /* body */
    vline(x + 14, y + 4, y + 18);
    hline(x + 1, x + 14, y + 19);     /* bottom */
    vline(x + 5, y + 7, y + 15);      /* ribs */
    vline(x + 8, y + 7, y + 15);
    vline(x + 11, y + 7, y + 15);
}

#define NF 6
static u8 fx[NF], fy[NF];
static signed char fvx[NF], fvy[NF];
static u8 ready;

static void fly(i32 x, i32 y)
{
    px(x, y);
    px(x - 1, y - 1); px(x + 1, y - 1);
    px(x - 1, y + 1); px(x + 1, y + 1);
}

void dtr_draw(void)
{
    i32 i;
    static u32 frame;
    if (PIT3_VEC != INTRO_ISR) return;
    fb = (u8 *)FBP;
    if (!fb) return;

    if (!ready) {
        for (i = 0; i < NF; i++) {
            fx[i] = (u8)(8 + (rnd() % 112u));
            fy[i] = (u8)(8 + (rnd() % 48u));
            fvx[i] = (signed char)((i32)(rnd() % 3u) - 1);
            fvy[i] = (signed char)((i32)(rnd() % 3u) - 1);
            if (!fvx[i] && !fvy[i]) fvx[i] = 1;
        }
        ready = 1;
    }

    for (i = 0; i < 1024; i++) fb[i] = 0;

    can(6, 20);
    {
        i32 jx = (i32)(rnd() % 3u) - 1;
        i32 jy = (i32)(rnd() % 3u) - 1;
        word((128 - 9 * 6) / 2 + jx, 26 + jy, "DIGITRASH");
    }

    for (i = 0; i < NF; i++) {
        i32 x = fx[i], y = fy[i];
        if ((rnd() & 7u) == 0u) {                 /* wander */
            i32 nvx = fvx[i] + (i32)(rnd() % 3u) - 1;
            i32 nvy = fvy[i] + (i32)(rnd() % 3u) - 1;
            if (nvx < -2) nvx = -2; if (nvx > 2) nvx = 2;
            if (nvy < -2) nvy = -2; if (nvy > 2) nvy = 2;
            if (!nvx && !nvy) nvx = 1;
            fvx[i] = (signed char)nvx;
            fvy[i] = (signed char)nvy;
        }
        if ((rnd() & 31u) == 0u) { fvx[i] = (signed char)((i32)(rnd() % 5u) - 2); fvy[i] = (signed char)((i32)(rnd() % 5u) - 2); }
        x += fvx[i];
        y += fvy[i];
        if (x < 4) { x = 4; fvx[i] = (signed char)(-fvx[i]); }
        if (x > 123) { x = 123; fvx[i] = (signed char)(-fvx[i]); }
        if (y < 4) { y = 4; fvy[i] = (signed char)(-fvy[i]); }
        if (y > 59) { y = 59; fvy[i] = (signed char)(-fvy[i]); }
        fx[i] = (u8)x; fy[i] = (u8)y;
        fly(x, y);
    }
    frame++;
}
