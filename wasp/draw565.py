import fonts.sans24
import micropython

@micropython.viper
def bitblit(bitbuf, pixels, bgfg: int, count: int):
    mv = ptr8(bitbuf)
    px = ptr8(pixels)

    bghi = (bgfg >> 24) & 0xff
    bglo = (bgfg >> 16) & 0xff
    fghi = (bgfg >>  8) & 0xff
    fglo = (bgfg      ) & 0xff

    bitselect = 0x80
    pxp = 0
    mvp = 0

    for bit in range(count):
        # Draw the pixel
        active = px[pxp] & bitselect
        mv[mvp] = fghi if active else bghi
        mvp += 1
        mv[mvp] = fglo if active else bglo
        mvp += 1

        # Advance to the next bit
        bitselect >>= 1
        if not bitselect:
            bitselect = 0x80
            pxp += 1

def bounding_box(s, font):
    w = 0
    for ch in s:
        (_, h, wc) = font.get_ch(ch)
        w += wc + 1

    return (w, h)

def draw_glyph(display, glyph, x, y, bgfg):
    (px, h, w) = glyph

    buf = memoryview(display.linebuffer)[0:2*(w+1)]
    bytes_per_row = (w + 7) // 8

    for row in range(h):
        bitblit(buf, px[row*bytes_per_row:], bgfg, w)
        buf[2*w] = 0
        buf[2*w + 1] = 0
        display.rawblit(buf, x, y+row, w+1, 1)

class Draw565(object):
    def __init__(self, display):
        self._display = display
        self.set_color(0xffff)
        self.set_font(fonts.sans24)

    def set_color(self, color, bg=0):
        self._bgfg = (bg << 16) + color

    def set_font(self, font):
        self._font = font

    def string(self, s, x, y, width=None):
        display = self._display
        bgfg = self._bgfg
        font = self._font

        if width:
            (w, h) = bounding_box(s, font)
            leftpad = (width - w) // 2
            rightpad = width - w - leftpad
            display.fill(0, x, y, leftpad, h)
            x += leftpad

        for ch in s:
            glyph = font.get_ch(ch)
            draw_glyph(display, glyph, x, y, bgfg)
            x += glyph[2] + 1

        if width:
            display.fill(0, x, y, rightpad, h)

#import watch
#draw = Draw(watch.display)
#
#def test():
#    watch.display.poweron()
#    watch.backlight.set(2)
#
#    draw.string('10-Jan-2020', 0, 24, width=240)
