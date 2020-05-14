# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 Daniel Thompson

"""Widget library
~~~~~~~~~~~~~~~~~

The widget library allows common fragments of logic and drawing code to be
shared between applications.
"""

import icons
import watch

class BatteryMeter(object):
    """Battery meter widget.

    A simple battery meter with a charging indicator, will draw at the
    top-right of the display.
    """
    def __init__(self):
        self.level = -2

    def draw(self):
        """Draw from meter (from scratch)."""
        self.level = -2
        self.update()

    def update(self):
        """Update the meter.

        The update is lazy and won't redraw unless the level has changed.
        """
        icon = icons.battery
        draw = watch.drawable

        if watch.battery.charging():
            if self.level != -1:
                draw.rleblit(icon, pos=(239-icon[0], 0), fg=0x7bef)
                self.level = -1
        else:
            level = watch.battery.level()
            if level == self.level:
                return

            if level > 96:
                h = 24
                rgb = 0x07e0
            else:
                h = level // 4

                green = level // 3
                red = 31-green
                rgb = (red << 11) + (green << 6)

            if (level > 5) ^ (self.level > 5):
                if level  > 5:
                    draw.rleblit(icon, pos=(239-icon[0], 0), fg=0x7bef)
                else:
                    rgb = 0xf800
                    draw.rleblit(icon, pos=(239-icon[0], 0), fg=0xf800)

            x = 239 - 30
            w = 16
            if 24 - h:
                draw.fill(0, x, 14, w, 24 - h)
            if h:
                draw.fill(rgb, x, 38 - h, w, h)

            self.level = level

class ScrollIndicator():
    """Scrolling indicator.

    A simple battery meter with a charging indicator, will draw at the
    top-right of the display.
    """
    def __init__(self, x=240-18, y=240-24):
        self._pos = (x, y)
        self.up = True
        self.down = True

    def draw(self):
        """Draw from scrolling indicator.

        For this simple widget :py:meth:`~.draw` is simply a synonym for
        :py:meth:`~.update`.
        """
        self.update()

    def update(self):
        """Update from scrolling indicator."""
        draw = watch.drawable
        if self.up:
            draw.rleblit(icons.up_arrow, pos=self._pos, fg=0x7bef)
        if self.down:
            draw.rleblit(icons.down_arrow, pos=(self._pos[0], self._pos[1] + 13), fg=0x7bef)
