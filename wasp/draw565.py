# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 Daniel Thompson

"""RGB565 drawing library
~~~~~~~~~~~~~~~~~~~~~~~~~
"""

import array
import fonts.sans24
import micropython

@micropython.viper
def _bitblit(bitbuf, pixels, bgfg: int, count: int):
    mv = ptr16(bitbuf)
    px = ptr8(pixels)

    # Extract and byte-swap
    bg = ((bgfg >> 24) & 0xff) + ((bgfg >> 8) & 0xff00)
    fg = ((bgfg >>  8) & 0xff) + ((bgfg & 0xff) << 8)

    bitselect = 0x80
    pxp = 0
    mvp = 0

    for bit in range(count):
        # Draw the pixel
        active = px[pxp] & bitselect
        mv[mvp] = fg if active else bg
        mvp += 1

        # Advance to the next bit
        bitselect >>= 1
        if not bitselect:
            bitselect = 0x80
            pxp += 1

@micropython.viper
def _clut8_rgb565(i: int) -> int:
    if i < 216:
        rgb565  = (( i  % 6) * 0x33) >> 3
        rg = i // 6
        rgb565 += ((rg  % 6) * (0x33 << 3)) & 0x07e0
        rgb565 += ((rg // 6) * (0x33 << 8)) & 0xf800
    elif i < 252:
        i -= 216
        rgb565  = (0x7f + (( i  % 3) * 0x33)) >> 3
        rg = i // 3
        rgb565 += ((0x4c << 3) + ((rg  % 4) * (0x33 << 3))) & 0x07e0
        rgb565 += ((0x7f << 8) + ((rg // 4) * (0x33 << 8))) & 0xf800
    else:
        i -= 252
        gr6 = (0x2c + (0x10 * i)) >> 2
        gr5 = gr6 >> 1
        rgb565 = (gr5 << 11) + (gr6 << 5) + gr5

    return rgb565

@micropython.viper
def _fill(mv, color: int, count: int, offset: int):
    p = ptr16(mv)
    color = (color >> 8) + ((color & 0xff) << 8)

    for x in range(offset, offset+count):
        p[x] = color

def _bounding_box(s, font):
    w = 0
    for ch in s:
        (_, h, wc) = font.get_ch(ch)
        w += wc + 1

    return (w, h)

@micropython.native
def _draw_glyph(display, glyph, x, y, bgfg):
    (px, h, w) = glyph

    buf = memoryview(display.linebuffer)[0:2*(w+1)]
    buf[2*w] = 0
    buf[2*w + 1] = 0
    bytes_per_row = (w + 7) // 8

    display.set_window(x, y, w+1, h)
    for row in range(h):
        _bitblit(buf, px[row*bytes_per_row:], bgfg, w)
        display.write_data(buf)

class Draw565(object):
    """Drawing library for RGB565 displays.

    A full framebufer is not required although the library will
    'borrow' a line buffer from the underlying display driver.

    .. automethod:: __init__
    """

    def __init__(self, display):
        """Initialise the library.

        Defaults to white-on-black for monochrome drawing operations
        and 24pt Sans Serif text.
        """
        self._display = display
        self.reset()

    def reset(self):
        """Restore the default colours and font.

        Default colours are white-on-block (white foreground, black
        background) and the default font is 24pt Sans Serif."""
        self.set_color(0xffff)
        self.set_font(fonts.sans24)

    def fill(self, bg=None, x=0, y=0, w=None, h=None):
        """Draw a solid colour rectangle.

        If no arguments a provided the whole display will be filled with
        the background colour (typically black).

        :param bg: Background colour (in RGB565 format)
        :param x:  X coordinate of the left-most pixels of the rectangle
        :param y:  Y coordinate of the top-most pixels of the rectangle
        :param w:  Width of the rectangle, defaults to None (which means select
                   the right-most pixel of the display)
        :param h:  Height of the rectangle, defaults to None (which means select
                   the bottom-most pixel of the display)
        """
        display = self._display
        quick_write = display.quick_write

        if bg is None:
            bg = self._bgfg >> 16
        if w is None:
            w = display.width - x
        if h is None:
            h = display.height - y

        display.set_window(x, y, w, h)

        remaining = w * h

        # Populate the line buffer
        buf = display.linebuffer
        sz = len(display.linebuffer) // 2
        _fill(buf, bg, min(sz, remaining), 0)

        display.quick_start()
        while remaining >= sz:
            quick_write(buf)
            remaining -= sz
        if remaining:
            quick_write(memoryview(display.linebuffer)[0:2*remaining])
        display.quick_end()

    @micropython.native
    def blit(self, image, x, y, fg=0xffff, c1=0x4a69, c2=0x7bef):
        """Decode and draw an encoded image.

        :param image: Image data in either 1-bit RLE or 2-bit RLE formats. The
                      format will be autodetected
        :param x: X coordinate for the left-most pixels in the image
        :param y: Y coordinate for the top-most pixels in the image
        """
        if len(image) == 3:
            # Legacy 1-bit image
            self.rleblit(image, (x, y), fg)
        else: #elif image[0] == 2:
            # 2-bit RLE image, (255x255, v1)
            self._rle2bit(image, x, y, fg, c1, c2)

    @micropython.native
    def rleblit(self, image, pos=(0, 0), fg=0xffff, bg=0):
        """Decode and draw a 1-bit RLE image.

        .. deprecated:: M2
            Use :py:meth:`~.blit` instead.
        """
        display = self._display
        write_data = display.write_data
        (sx, sy, rle) = image

        display.set_window(pos[0], pos[1], sx, sy)

        buf = memoryview(display.linebuffer)[0:2*sx]
        bp = 0
        color = bg

        for rl in rle:
            while rl:
                count = min(sx - bp, rl)
                _fill(buf, color, count, bp)
                bp += count
                rl -= count

                if bp >= sx:
                    write_data(buf)
                    bp = 0

            if color == bg:
                color = fg
            else:
                color = bg

    @micropython.native
    def _rle2bit(self, image, x, y, fg, c1, c2):
        """Decode and draw a 2-bit RLE image."""
        display = self._display
        quick_write = display.quick_write
        sx = image[1]
        sy = image[2]
        rle = memoryview(image)[3:]

        display.set_window(x, y, sx, sy)

        if sx <= (len(display.linebuffer) // 4) and not bool(sy & 1):
            sx *= 2
            sy //= 2

        palette = array.array('H', (0, c1, c2, fg))
        next_color = 1
        rl = 0
        buf = memoryview(display.linebuffer)[0:2*sx]
        bp = 0

        display.quick_start()
        for op in rle:
            if rl == 0:
                px = op >> 6
                rl = op & 0x3f
                if 0 == rl:
                    rl = -1
                    continue
                if rl >= 63:
                    continue
            elif rl > 0:
                rl += op
                if op >= 255:
                    continue
            else:
                palette[next_color] = _clut8_rgb565(op)
                if next_color < 3:
                    next_color += 1
                else:
                    next_color = 1
                rl = 0
                continue

            while rl:
                count = min(sx - bp, rl)
                _fill(buf, palette[px], count, bp)
                bp += count
                rl -= count

                if bp >= sx:
                    quick_write(buf)
                    bp = 0
        display.quick_end()

    def set_color(self, color, bg=0):
        """Set the foreground and background colours.

        The supplied colour will be used for all monochrome drawing operations.
        If no background colour is provided then the background will be set
        to black.

        :param color: Foreground colour
        :param bg:    Background colour, defaults to black
        """
        self._bgfg = (bg << 16) + color

    def set_font(self, font):
        """Set the font used for rendering text.

        :param font:  A font module generated using ``font_to_py.py``.
        """
        self._font = font

    def string(self, s, x, y, width=None):
        """Draw a string at the supplied position.

        :param s:     String to render
        :param x:     X coordinate for the left-most pixels in the image
        :param y:     Y coordinate for the top-most pixels in the image
        :param width: If no width is provided then the text will be left
                      justified, otherwise the text will be centred within the
                      provided width and, importantly, the remaining width will
                      be filled with the background colour (to ensure that if
                      we update one string with a narrower one there is no
                      need to "undraw" it)
        """
        display = self._display
        bgfg = self._bgfg
        font = self._font
        bg = self._bgfg >> 16

        if width:
            (w, h) = _bounding_box(s, font)
            leftpad = (width - w) // 2
            rightpad = width - w - leftpad
            self.fill(bg, x, y, leftpad, h)
            x += leftpad

        for ch in s:
            glyph = font.get_ch(ch)
            _draw_glyph(display, glyph, x, y, bgfg)
            self.fill(bg, x+glyph[2], y, 1, glyph[1])
            x += glyph[2] + 1

        if width:
            self.fill(bg, x, y, rightpad, h)

    def wrap(self, s, width):
        """Chunk a string so it can rendered within a specified width.

        Example:

        .. code-block:: python

            draw = wasp.watch.drawable
            chunks = draw.wrap(long_string, 240)

            # line(1) will provide the first line
            # line(len(chunks)-1) will provide the last line
            def line(n):
                return long_string[chunks[n-1]:chunks[n]]

        :param s:     String to be chunked
        :param width: Width to wrap the text into
        :returns:     List of chunk boundaries
        """
        font = self._font
        max = len(s)
        chunks = [ 0, ]
        end = 0

        while end < max:
            start = end
            l = 0

            for i in range(start, max+1):
                if i >= len(s):
                    break
                ch = s[i]
                if ch == '\n':
                    end = i+1
                    break
                if ch == ' ':
                    end = i+1
                (_, h, w) = font.get_ch(ch)
                l += w + 1
                if l > width:
                    break
            if end <= start:
                end = i
            chunks.append(end)

        return chunks
