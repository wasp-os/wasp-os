# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 Daniel Thompson

"""Analogue clock
~~~~~~~~~~~~~~~~~

Shows the time as a traditional watch face together with a battery meter.

.. figure:: res/screenshots/ChronoApp.png
    :width: 179

    Screenshot of the analogue clock application
"""

import wasp

class ChronoApp():
    """Simple analogue clock application.
    """
    NAME = 'Chrono'

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
        """Draw or lazily update the display.

        The updates are as lazy by default and avoid spending time redrawing
        if the time on display has not changed. However if redraw is set to
        True then a full redraw is be performed.
        """
        draw = wasp.watch.drawable
        hi = wasp.system.theme('bright')
        c1 = draw.darken(wasp.system.theme('spot1'), wasp.system.theme('contrast'))

        if redraw:
            now = wasp.watch.rtc.get_localtime()

            # Clear the display and draw that static parts of the watch face
            draw.fill()

            # Redraw the status bar
            wasp.system.bar.draw()

            # Draw the dividers
            draw.set_color(wasp.system.theme('mid'))
            for theta in range(12):
                draw.polar(120, 120, theta * 360 // 12, 110, 118, 3)

            self._hh = 0
            self._mm = 0
        else:
            now = wasp.system.bar.update()
            if not now or self._mm == now[4]:
                # Skip the update
                return

        # Undraw old time
        hh = (30 * (self._hh % 12)) + (self._mm / 2)
        mm = 6 * self._mm
        draw.polar(120, 120, hh, 5, 75, 7, 0)
        draw.polar(120, 120, mm, 5, 106, 5, 0)

        # Record the minute that is currently being displayed
        self._hh = now[3]
        self._mm = now[4]

        # Draw the new time
        hh = (30 * (self._hh % 12)) + (self._mm / 2)
        mm = 6 * self._mm
        draw.polar(120, 120, hh, 5, 75, 7, hi)
        draw.polar(120, 120, hh, 5, 60, 3, draw.darken(c1, 2))
        draw.polar(120, 120, mm, 5, 106, 5, hi)
