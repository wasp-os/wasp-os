# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 Daniel Thompson

import wasp

class FlashlightApp(object):
    """Trivial flashlight application.

    Shows a pure white screen with the backlight set to maximum.
    """

    def foreground(self):
        """Activate the application."""
        self.on_screen = ( -1, -1, -1, -1, -1, -1 )
        self.draw()
        wasp.system.request_tick(1000)

        self._brightness = wasp.system.brightness
        wasp.system.brightness = 3

    def background(self):
        """De-activate the application (without losing state)."""
        wasp.system.brightness = self._brightness

    def sleep(self):
        return False

    def tick(self, ticks):
        wasp.system.keep_awake()

    def draw(self):
        """Redraw the display from scratch."""
        display = wasp.watch.display
        display.fill(0xffff)
