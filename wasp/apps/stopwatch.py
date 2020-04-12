# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 Daniel Thompson

import wasp
import icons

class StopwatchApp():
    NAME = 'Stopwatch'
    ICON = icons.app

    def foreground(self):
        """Activate the application."""
        self._draw()

    def _draw(self):
        """Draw the display from scratch."""
        draw = wasp.watch.drawable
        draw.fill()
        draw.string(self.NAME, 0, 6, width=240)
