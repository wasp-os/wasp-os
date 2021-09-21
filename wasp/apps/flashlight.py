# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 Daniel Thompson

"""Flashlight
~~~~~~~~~~~~~

Shows a pure white screen with the backlight set to maximum.

.. figure:: res/TorchApp.png
    :width: 179
"""

import wasp

import icons

class TorchApp(object):
    """Trivial flashlight application."""
    NAME = 'Torch'
    ICON = icons.torch

    def __init__(self):
        self.__activated = False

    def foreground(self):
        """Activate the application."""
        self._brightness = wasp.system.brightness
        self.draw()
        wasp.system.request_tick(1000)
        wasp.system.request_event(wasp.EventMask.TOUCH | wasp.EventMask.BUTTON)

    def background(self):
        """De-activate the application (without losing state)."""
        self.__activated = False
        wasp.system.brightness = self._brightness

    def tick(self, ticks):
        wasp.system.keep_awake()

    def touch(self, event):
        self.__activated = not self.__activated
        self.draw()

    def press(self, button, state):
        if not state:
            return

        self.__activated = not self.__activated
        self.draw()

    def draw(self):
        """Redraw the display from scratch."""
        white = 0xffff
        draw = wasp.watch.drawable

        if self.__activated:
            draw.fill(white)
            wasp.system.brightness = 3

        else:
            draw.fill()
            wasp.system.brightness = self._brightness

            x = 108
            mid = wasp.system.theme('mid')

            draw.fill(mid, x, 107, 24, 9)
            for i in range(1, 8):
                draw.line(x+i, 115+i, x+23-i, 115+i, color=mid)
            draw.fill(mid, x+8, 123, 8, 15)

            draw.line(x-3, 94, x+5, 102, 2, white)
            draw.line(x+17, 102, x+25, 94, 2, white)
            draw.line(x+11, 89, x+11, 100, 2, white)
