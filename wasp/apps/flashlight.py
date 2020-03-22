# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 Daniel Thompson

import wasp

class FlashlightApp(object):
    """Trivial flashlight application.

    Shows a pure white screen with the backlight set to maximum.
    """

    def __init__(self):
        self.backlight = None

    def foreground(self, effect=None):
        """Activate the application."""
        self.on_screen = ( -1, -1, -1, -1, -1, -1 )
        self.draw(effect)
        wasp.system.request_tick(1000)

    def background(self):
        """De-activate the application (without losing state)."""
        pass

    def sleep(self):
        return False

    def tick(self, ticks):
        pass

    def draw(self, effect=None):
        """Redraw the display from scratch."""
        display = wasp.watch.display
        display.fill(0xffff)
