# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 Daniel Thompson

"""Digital clock
~~~~~~~~~~~~~~~~

Shows a time (as HH:MM) together with a battery meter and the date.

.. figure:: res/screenshots/ClockApp.png
    :width: 179
"""

import wasp

import fonts.clock as digits

DIGITS = (
        digits.clock_0, digits.clock_1, digits.clock_2, digits.clock_3,
        digits.clock_4, digits.clock_5, digits.clock_6, digits.clock_7,
        digits.clock_8, digits.clock_9
)

MONTH = 'JanFebMarAprMayJunJulAugSepOctNovDec'

class ClockApp():
    """Simple digital clock application."""
    NAME = 'Clock'

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

    def _day_string(self, now):
        """Produce a string representing the current day"""
        # Format the month as text
        month = now[1] - 1
        month = MONTH[month*3:(month+1)*3]

        return '{} {} {}'.format(now[2], month, now[0])

    def _draw(self, redraw=False):
        """Draw or lazily update the display.

        The updates are as lazy by default and avoid spending time redrawing
        if the time on display has not changed. However if redraw is set to
        True then a full redraw is be performed.
        """
        draw = wasp.watch.drawable
        hi =  wasp.system.theme('bright')
        lo =  wasp.system.theme('mid')
        mid = draw.lighten(lo, 1)

        now = wasp.watch.rtc.get_localtime()

        if redraw:
            # Clear the display and draw that static parts of the watch face
            draw.fill()
            draw.blit(digits.clock_colon, 2*48, 80, fg=mid)

            # Redraw the status bar
            wasp.system.bar.draw()
        else:
            # Redraw the status bar if necessary. This does not overlap the
            # other elements on the screen.
            wasp.system.bar.update()

            # Only continue drawing if the minute has changed.
            if self._min == now[4]:
                return

        # Draw the changeable parts of the watch face
        draw.blit(DIGITS[now[4]  % 10], 4*48, 80, fg=hi)
        draw.blit(DIGITS[now[4] // 10], 3*48, 80, fg=lo)
        draw.blit(DIGITS[now[3]  % 10], 1*48, 80, fg=hi)
        draw.blit(DIGITS[now[3] // 10], 0*48, 80, fg=lo)
        draw.set_color(hi)
        draw.string(self._day_string(now), 0, 180, width=240)

        # Record the minute that is currently being displayed
        self._min = now[4]
