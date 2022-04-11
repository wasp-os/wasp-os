# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 Daniel Thompson

"""Flashlight
~~~~~~~~~~~~~

Shows a bright screen that you can tap to change brightness or switch to redlight.

.. figure:: res/TorchApp.png
    :width: 179
"""

import wasp
import icons

class TorchApp(object):
    """Trivial flashlight application."""
    NAME = 'Torch'
    ICON = icons.torch

    def foreground(self):
        """Activate the application."""
        wasp.system.request_tick(1000)
        wasp.system.request_event(wasp.EventMask.TOUCH)

        self._brightness = wasp.system.brightness
        wasp.system.brightness = 3
        self.n_touch = 0
        self.draw()

    def background(self):
        """De-activate the application (without losing original state)."""
        wasp.system.brightness = self._brightness

    def tick(self, ticks):
        wasp.system.keep_awake()

    def draw(self):
        """Redraw the display from scratch."""
        if self.n_touch % 6 < 3:
            wasp.watch.drawable.fill(0xffff)
        else:
            wasp.watch.drawable.fill(0xf800)
        print("ok")

    def touch(self, event):
        self.n_touch += 1
        n = (wasp.system.brightness - 1) % 3
        wasp.system.brightness = n if n else 3
        self.draw()
