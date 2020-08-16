# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 Daniel Thompson

"""Flashlight
~~~~~~~~~~~~~

Shows a pure white screen with the backlight set to maximum.
"""

import wasp

import icons

class FlashlightApp(object):
    """Trivial flashlight application.

    .. figure:: res/TorchApp.png
        :width: 179

        Screenshot of the flashlight application
    """
    NAME = 'Torch'
    ICON = icons.torch

    def foreground(self):
        """Activate the application."""
        self.draw()
        wasp.system.request_tick(1000)

        self._brightness = wasp.system.brightness
        wasp.system.brightness = 3

    def background(self):
        """De-activate the application (without losing state)."""
        wasp.system.brightness = self._brightness

    def tick(self, ticks):
        wasp.system.keep_awake()

    def draw(self):
        """Redraw the display from scratch."""
        wasp.watch.drawable.fill(0xffff)
