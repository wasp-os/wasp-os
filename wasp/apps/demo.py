# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 Daniel Thompson

"""Logo demo for PineTime
~~~~~~~~~~~~~~~~~~~~~~~~~

This demo is simply an alternating sweep of the Pine64 and
MicroPython logos. It cycles through a variety of colours
and swaps between the logos every 5 images (so if you change
anything make sure len(colors) is not a multiple of 5).
"""

import wasp
import logo
import icons

colors = (
        0xffff,
        0xf800, # red
        0xffff,
        0xffe0, # yellow
        0xffff,
        0x07e0, # green
        0xffff,
        0x07ff, # cyan
        0xffff,
        0x001f, # blue
        0xffff,
        0xf81f, # magenta
    )

class DemoApp():
    """Application for live demos.

    Start this to give the watch something "interesting" to do when talking
    over demos!
    """
    NAME = 'Demo'
    ICON = icons.app

    def __init__(self):
        self._logo = logo.pine64
        self._color = 0
        self._i = 0

    def foreground(self):
        """Draw the first frame and establish the tick."""
        self._draw()
        wasp.system.request_tick(2000)

    def tick(self, ticks):
        """Handle the tick."""
        self._draw()
        wasp.system.keep_awake()

    def _draw(self):
        """Draw the next frame."""
        draw = wasp.watch.drawable

        if self._i < 5:
            self._i += 1
        else:
            self._i = 0
            if self._logo == logo.pine64:
                self._logo = logo.micropython
            else:
                self._logo = logo.pine64
            draw.fill()
        draw.rleblit(self._logo, fg=colors[self._color])
        self._color += 1
        if self._color >= len(colors):
            self._color = 0
