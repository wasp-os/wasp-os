# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2023 Tony Robinson based on the other WASP-OS clock faces
"""Resistor Clock Face
~~~~~~~~~~~~~~~~~~~~~~

Following https://hackaday.com/2021/07/15/a-perfect-clock-for-any-hackers-ohm
display the time as HHMMSS DDMMYYY in 6+8 bands using the resistor colour code.

This is very good if you want to learn the resistor colour codes, you pick them up very rapidly.

Colours taken from https://people.duke.edu/~ng46/topics/color-code.htm (grey moved from CCCCCC to C0C0C0)

Code adapted from fibonacci_clock.py by Johannes Wache
Display the time in using the resistor colour codes

.. figure:: res/screenshots/ResistorClockApp.png
    :width: 179
"""

import wasp

_COLOR = [ 0x0000, 0x9B26, 0xF800, 0xFCC0, 0xFFE0, 0x07E0, 0x001F, 0xF81F, 0xC618, 0xFFFF ]
_TIMEX = bytearray([0, 40, 83, 123, 166, 206])
_DATEX = bytearray([0, 30, 63, 93, 126, 156, 186, 216])

class ResistorClockApp():
    NAME = 'Resist'

    def foreground(self):
        """Activate the application.

        Configure the status bar, redraw the display and request a periodic
        tick callback every second.
        """
        wasp.system.bar.clock = False
        self._draw(True)
        wasp.system.request_tick(1000)

    def sleep(self):
        """Prepare to enter the low power mode.

        :returns: True, which tells the system manager not to automatically
                  switch to the default application before sleeping.
        """
        return True

    def wake(self):
        """Return from low power mode.

        Time will have changes whilst we have been asleep so we must
        udpate the display (but there is no need for a full redraw because
        the display RAM is preserved during a sleep.
        """
        self._draw()

    def tick(self, ticks):
        """Periodic callback to update the display."""
        self._draw()

    def preview(self):
        """Provide a preview for the watch face selection."""
        wasp.system.bar.clock = False
        self._draw(True)

    def _draw(self, redraw=False):
        """Draw or lazily update the display."""

        draw = wasp.watch.drawable

        if redraw:
            now = wasp.watch.rtc.get_localtime()
            draw.fill()
            wasp.system.bar.draw()
        else:
            now = wasp.system.bar.update()
            if not now:  # or self._sec == now[5]:
                return

        # draw time
        for i, c in enumerate('%02d%02d%02d' % now[3:6]):
          draw.fill(x=_TIMEX[i],y=60,w=34,h=80,bg=_COLOR[int(c)])

        # draw date
        for i, c in enumerate('%02d%02d%04d' % (now[2], now[1], now[0])):
          draw.fill(x=_DATEX[i],y=180,w=24,h=60,bg=_COLOR[int(c)])
          
        # Record the second that is currently being displayed
        # self._sec = now[5]
