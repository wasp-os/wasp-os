# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 Daniel Thompson

"""Digital dual clock
~~~~~~~~~~~~~~~~~~~~~~~~

Shows a time (as HH and MM vertically) together with a battery meter.

.. figure:: res/screenshots/DualClockApp.png
    :width: 179
"""

import wasp

import fonts.clock_dual as digits

DIGITS = (
    digits.clock_dual_0, digits.clock_dual_1, digits.clock_dual_2, digits.clock_dual_3,
    digits.clock_dual_4, digits.clock_dual_5, digits.clock_dual_6, digits.clock_dual_7,
    digits.clock_dual_8, digits.clock_dual_9
)


class DualClockApp():
    """Simple digital clock application."""
    NAME = 'Dual'
    _min = None

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
        lo = wasp.system.theme('mid')

        now = wasp.watch.rtc.get_localtime()

        if redraw:
            # Clear the display and draw that static parts of the watch face
            draw.fill()
            #draw.blit(digits.clock_colon, 2*48, 80, fg=mid)

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
        draw.blit(DIGITS[now[4] % 10], 40 + 1*90, 140, fg=hi)
        draw.blit(DIGITS[now[4] // 10], 40 + 0*90, 140, fg=hi)
        draw.blit(DIGITS[now[3] % 10], 40 + 1*90, 40, fg=lo)
        draw.blit(DIGITS[now[3] // 10], 40 + 0*90, 40, fg=lo)
        #draw.roundRect(25, 135, 180, 100, 5, lo)
        # Record the minute that is currently being displayed
        self._min = now[4]
