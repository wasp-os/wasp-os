# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 Daniel Thompson

"""Sitronix ST7789 display driver
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. note::

    Although the ST7789 supports a variety of communication protocols currently
    this driver only has support for SPI interfaces. However it is structured
    such that other serial protocols can easily be added.
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
    """Sitronix ST7789 display driver

    .. automethod:: __init__
    """
    def __init__(self, width, height):
        """Configure the size of the display.

        :param int width: Display width, in pixels
        :param int height: Display height in pixels
        """
        self.width = width
        self.height = height
        self.linebuffer = bytearray(2 * width)
        self.init_display()

    def init_display(self):
        """Reset and initialize the display."""
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
        # (i.e. when the SPI baud rate is slower than 8M then
        # that time already elapsed as we zeroed the RAM).
        #sleep_ms(125)

    def poweroff(self):
        """Put the display into sleep mode."""
        self.write_cmd(_SLPIN)
        sleep_ms(125)

    def poweron(self):
        """Wake the display and leave sleep mode."""
        self.write_cmd(_SLPOUT)
        sleep_ms(125)

    def invert(self, invert):
        """Invert the display.

        :param bool invert: True to invert the display, False for normal mode.
        """
        if invert:
            self.write_cmd(_INVON)
        else:
            self.write_cmd(_INVOFF)

    def mute(self, mute):
        """Mute the display.

        When muted the display will be entirely black.

        :param bool mute: True to mute the display, False for normal mode.
        """
        if mute:
            self.write_cmd(_DISPOFF)
        else:
            self.write_cmd(_DISPON)

    def set_window(self, x=0, y=0, width=None, height=None):
        """Set the clipping rectangle.

        All writes to the display will be wrapped at the edges of the rectangle.

        :param x:  X coordinate of the left-most pixels of the rectangle
        :param y:  Y coordinate of the top-most pixels of the rectangle
        :param w:  Width of the rectangle, defaults to None (which means select
                   the right-most pixel of the display)
        :param h:  Height of the rectangle, defaults to None (which means select
                   the bottom-most pixel of the display)
        """
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
        """Blit raw pixels to the display.

        :param buf: Pixel buffer
        :param x:  X coordinate of the left-most pixels of the rectangle
        :param y:  Y coordinate of the top-most pixels of the rectangle
        :param w:  Width of the rectangle, defaults to None (which means select
                   the right-most pixel of the display)
        :param h:  Height of the rectangle, defaults to None (which means select
                   the bottom-most pixel of the display)
        """
        self.set_window(x, y, width, height)
        self.write_data(buf)

    def fill(self, bg, x=0, y=0, w=None, h=None):
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
    """
    .. method:: quick_write(buf)

        Send data to the display as part of an optimized write sequence.

        :param bytearray buf: Data, must be in a form that can be directly
                              consumed by the SPI bus.
    """
    def __init__(self, width, height, spi, cs, dc, res=None, rate=8000000):
        """Configure the display.

        :param int width: Width of the display
        :param int height: Height of the display
        :param machine.SPI spi: SPI controller
        :param machine.Pin cs: Pin (or signal) to use as the chip select
        :param machine.Pin cs: Pin (or signal) to use to switch between data
                               and command mode.
        :param machine.Pin res: Pin (or signal) to, optionally, use to reset
                                the display.
        :param int rate: SPI bus frequency
        """
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
        """Reset the display.

        Uses the hardware reset pin if there is one, otherwise it will issue
        a software reset command.
        """
        if self.res:
            self.res(0)
            sleep_ms(10)
            self.res(1)
        else:
            self.write_cmd(_SWRESET)
        sleep_ms(125)

    def write_cmd(self, cmd):
        """Send a command opcode to the display.

        :param sequence cmd: Command, will be automatically converted so it can
                             be issued to the SPI bus.
        """
        dc = self.dc
        cs = self.cs

        dc(0)
        cs(0)
        self.quick_write(bytearray([cmd]))
        cs(1)
        dc(1)

    def write_data(self, buf):
        """Send data to the display.

        :param bytearray buf: Data, must be in a form that can be directly
                              consumed by the SPI bus.
        """
        cs = self.cs
        cs(0)
        self.quick_write(buf)
        cs(1)

    def quick_start(self):
        """Prepare for an optimized write sequence.

        Optimized write sequences allow applications to produce data in chunks
        without having any overhead managing the chip select.
        """
        self.cs(0)

    def quick_end(self):
        """Complete an optimized write sequence."""
        self.cs(1)
