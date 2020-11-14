# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 Daniel Thompson

"""Digital clock
~~~~~~~~~~~~~~~~

Shows a time (as HH:MM) together with a battery meter and the date.
"""

import wasp

import icons
import fonts.clock as digits

DIGITS = (
        digits.clock_0, digits.clock_1, digits.clock_2, digits.clock_3,
        digits.clock_4, digits.clock_5, digits.clock_6, digits.clock_7,
        digits.clock_8, digits.clock_9
)

MONTH = 'JanFebMarAprMayJunJulAugSepOctNovDec'

class ClockApp():
    """Simple digital clock application.

    .. figure:: res/ClockApp.png
        :width: 179

        Screenshot of the clock application
    """
    NAME = 'Clock'
    ICON = icons.clock

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

    def _draw(self, redraw=False):
        """Draw or lazily update the display.

        The updates are as lazy by default and avoid spending time redrawing
        if the time on display has not changed. However if redraw is set to
        True then a full redraw is be performed.
        """
        draw = wasp.watch.drawable

        if redraw:
            now = wasp.watch.rtc.get_localtime()

            # Clear the display and draw that static parts of the watch face
            draw.fill()
            draw.rleblit(digits.clock_colon, pos=(2*48, 80), fg=0xb5b6)

            # Redraw the status bar
            wasp.system.bar.draw()
        else:
            # The update is doubly lazy... we update the status bar and if
            # the status bus update reports a change in the time of day 
            # then we compare the minute on display to make sure we 
            # only update the main clock once per minute.
            now = wasp.system.bar.update()
            if not now or self._min == now[4]:
                # Skip the update
                return

        # Format the month as text
        month = now[1] - 1
        month = MONTH[month*3:(month+1)*3]

        # Draw the changeable parts of the watch face
        draw.rleblit(DIGITS[now[4]  % 10], pos=(4*48, 80))
        draw.rleblit(DIGITS[now[4] // 10], pos=(3*48, 80), fg=0xbdb6)
        draw.rleblit(DIGITS[now[3]  % 10], pos=(1*48, 80))
        draw.rleblit(DIGITS[now[3] // 10], pos=(0*48, 80), fg=0xbdb6)
        draw.string('{} {} {}'.format(now[2], month, now[0]),
                0, 180, width=240)

        # Record the minute that is currently being displayed
        self._min = now[4]
