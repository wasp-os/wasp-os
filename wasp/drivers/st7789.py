# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 Daniel Thompson

"""Sitronix ST7789 display driver for MicroPython.

Note: Although the ST7789 supports a variety of communication protocols
currently this driver only has support for SPI interfaces. However it is
structured such that other serial protocols can easily be added.
"""

import micropython

from micropython import const
from time import sleep_ms

# register definitions
_SWRESET            = const(0x01)
_SLPIN              = const(0x10)
_SLPOUT             = const(0x11)
_NORON              = const(0x13)
_INVOFF             = const(0x20)
_INVON              = const(0x21)
_DISPOFF            = const(0x28)
_DISPON             = const(0x29)
_CASET              = const(0x2a)
_RASET              = const(0x2b)
_RAMWR              = const(0x2c)
_COLMOD             = const(0x3a)
_MADCTL             = const(0x36)

class ST7789(object):
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.linebuffer = bytearray(2 * width)
        self.init_display()

    def init_display(self):
        self.reset()

        self.write_cmd(_SLPOUT)
        sleep_ms(10)

        for cmd in (
            (_COLMOD,   b'\x05'), # MCU will send 16-bit RGB565
            (_MADCTL,   b'\x00'), # Left to right, top to bottom
            #(_INVOFF,   None), # Results in odd palette
            (_INVON,   None),
            (_NORON,   None),
        ):
            self.write_cmd(cmd[0])
            if cmd[1]:
                self.write_data(cmd[1])
        self.fill(0)
        self.write_cmd(_DISPON)

        # From the point we sent the SLPOUT there must be a
        # 120ms gap before any subsequent SLPIN. In most cases
        # (i.e. wen the SPI baud rate is slower than 8M then
        # that time already elapsed as we zeroed the RAM).
        #sleep_ms(125)

    def poweroff(self):
        self.write_cmd(_SLPIN)
        sleep_ms(125)

    def poweron(self):
        self.write_cmd(_SLPOUT)
        sleep_ms(125)

    def contrast(self, contrast):
        pass

    def invert(self, invert):
        if invert:
            self.write_cmd(_INVON)
        else:
            self.write_cmd(_INVOFF)

    def mute(self, mute):
        if mute:
            self.write_cmd(_DISPOFF)
        else:
            self.write_cmd(_DISPON)

    def set_window(self, x=0, y=0, width=None, height=None):
        if not width:
            width = self.width
        if not height:
            height = self.height

        xp = x + width - 1
        yp = y + height - 1

        self.write_cmd(_CASET)
        self.write_data(bytearray([x >> 8, x & 0xff, xp >> 8, xp & 0xff]))
        self.write_cmd(_RASET)
        self.write_data(bytearray([y >> 8, y & 0xff, yp >> 8, yp & 0xff]))
        self.write_cmd(_RAMWR)

    def rawblit(self, buf, x, y, width, height):
        self.set_window(x, y, width, height)
        self.write_data(buf)

    def fill(self, bg, x=0, y=0, w=None, h=None):
        if not w:
            w = self.width - x
        if not h:
            h = self.height - y
        self.set_window(x, y, w, h)

        # Populate the line buffer
        buf = memoryview(self.linebuffer)[0:2*w]
        for xi in range(0, 2*w, 2):
            buf[xi] = bg >> 8
            buf[xi+1] = bg & 0xff

        # Do the fill
        for yi in range(h):
            self.write_data(buf)

class ST7789_SPI(ST7789):
    def __init__(self, width, height, spi, cs, dc, res=None, rate=8000000):
        self.quick_write = spi.write
        self.cs = cs.value
        self.dc = dc.value
        self.res = res
        self.rate = rate

        #spi.init(baudrate=self.rate, polarity=1, phase=1)
        cs.init(cs.OUT, value=1)
        dc.init(dc.OUT, value=0)
        if res:
            res.init(res.OUT, value=0)

        super().__init__(width, height)

    def reset(self):
        if self.res:
            self.res(0)
            sleep_ms(10)
            self.res(1)
        else:
            self.write_cmd(_SWRESET)
        sleep_ms(125)

    def write_cmd(self, cmd):
        dc = self.dc
        cs = self.cs

        dc(0)
        cs(0)
        self.quick_write(bytearray([cmd]))
        cs(1)
        dc(1)

    def write_data(self, buf):
        cs = self.cs
        cs(0)
        self.quick_write(buf)
        cs(1)

    def quick_start(self):
        self.cs(0)

    def quick_end(self):
        self.cs(1)
