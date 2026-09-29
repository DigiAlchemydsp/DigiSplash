/* SPDX-License-Identifier: GPL-2.0-or-later
 * DigiTussy: the DIGITUSSY wordmark bobbing over rising particles.
 *
 * Called once per panel present while the intro owns PIT3. The panel is
 * 128x64, 1bpp, byte = page + 8*column, page = 7 - (y>>3), bit = y&7.
 */
typedef unsigned char u8;
typedef unsigned int u32;
typedef int i32;

#define FBP      (*(volatile u32 *)0x4020d8f8)
#define PIT3_VEC (*(volatile u32 *)0x40000340)
#define INTRO_ISR ((u32)0x4006c154)

static u8 *fb;

/* 5x7, column-major, bit 0 = top row */
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

static u32 rs = 0x2545f491u;
static u32 rnd(void) { rs = rs * 1103515245u + 12345u; return (rs >> 16) & 0x7fffu; }

static void px(i32 x, i32 y)
{
    if (y < 0 || x < 0 || x > 127 || y > 63) return;
    fb[(7 - (y >> 3)) + (x << 3)] |= (u8)(1u << (y & 7));
}

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

#define NP 64
static u8 ppx[NP], ppy[NP];
static signed char pvx[NP], pvy[NP];
static u8 ready;

static i32 tri(i32 f, i32 period, i32 amp)
{
    i32 t = f % (2 * period);
    if (t < 0) t += 2 * period;
    if (t > period) t = 2 * period - t;
    return (t * amp) / period;
}

void dt_draw(void)
{
    i32 i;
    static u32 frame;
    if (PIT3_VEC != INTRO_ISR) return;
    fb = (u8 *)FBP;
    if (!fb) return;

    if (!ready) {
        for (i = 0; i < NP; i++) {
            ppx[i] = (u8)(rnd() & 127u);
            ppy[i] = (u8)(rnd() & 63u);
            pvx[i] = (signed char)((i32)(rnd() % 5u) - 2);
            pvy[i] = (signed char)(1 + (i32)(rnd() % 3u));
        }
        ready = 1;
    }

    for (i = 0; i < 1024; i++) fb[i] = 0;

    {
        i32 bob = tri((i32)frame, 16, 4) - 2;
        i32 x0 = (128 - 8 * 6) / 2;
        word(x0, 23 + bob, "DIGITUSSY");
        /* flickering underline "glitter" */
        if ((frame & 3u) == 0u) {
            i32 k;
            for (k = 0; k < 10; k++) {
                i32 lx = x0 + (i32)(rnd() % 48u);
                i32 ly = 32 + bob + (i32)(rnd() % 4u);
                px(lx, ly);
            }
        }
    }

    for (i = 0; i < NP; i++) {
        i32 x = ppx[i], y = ppy[i];
        x += pvx[i];
        y -= pvy[i];
        if (x < 0) x += 128; else if (x > 127) x -= 128;
        if (y < 0) { y = 63; x = (i32)(rnd() & 127u); }
        ppx[i] = (u8)x; ppy[i] = (u8)y;
        px(x, y);
        if (y & 1) px(x, y + 1);
    }
    frame++;
}
