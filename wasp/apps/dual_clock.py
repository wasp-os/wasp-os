# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 Daniel Thompson

"""Digital dual clock
~~~~~~~~~~~~~~~~~~~~~~~~

Shows a time (as HH and MM vertically) together with a battery meter.

.. figure:: res/DualApp.png
    :width: 179
"""

import wasp

import icons
import fonts.clock_dual as digits

DIGITS = (
    digits.clock_dual_0, digits.clock_dual_1, digits.clock_dual_2, digits.clock_dual_3,
    digits.clock_dual_4, digits.clock_dual_5, digits.clock_dual_6, digits.clock_dual_7,
    digits.clock_dual_8, digits.clock_dual_9
)


class DualClockApp():
    """Simple digital clock application."""
    NAME = 'Dual'
    # 2-bit RLE, generated from clock_dual_icon.png, 298 bytes
    ICON = (
        b'\x02'
        b'`@'
        b'?\xff\xc1@\xacF\r\xc6?\x06H\x0b\xca?\x04H'
        b'\n\xcc?\x03C\x02C\n\xc4\x05\xc4?\x07C\t\xc4'
        b'\x07\xc3?\x07C\t\xc3\t\xc2?\x07C\t\xc3\t\xc3'
        b'?\x06C\t\xc3\t\xc3?\x06C\t\xc3\t\xc3?\x06'
        b'C\t\xc4\x07\xc4?\x06C\n\xc4\x05\xc5?\x06C\n'
        b'\xca\x01\xc3?\x06C\x0b\xc9\x01\xc3?\x06C\r\xc5\x03'
        b'\xc3?\x06C\x15\xc3?\x06C\x14\xc4?\x06C\x14\xc3'
        b'?\x07C\x14\xc3?\x07C\x13\xc4?\x07C\x0b\xc1\x05'
        b'\xc5?\x03M\x06\xca?\x04M\x06\xc9?\x05M\x07\xc6'
        b'?\xff\xedE\x0b\xc8?\x07I\x07\xcc?\x04K\x06\xce'
        b'?\x02D\x03D\x06\xc2\x08\xc4?\x01D\x05D\x10\xc4'
        b'?\x00C\x07C\x11\xc3>D\x07D\x10\xc3>C\t'
        b'C\x10\xc3>C\tC\x10\xc3>C\tC\x0f\xc4>'
        b'C\tC\x0e\xc4?\x00C\tC\r\xc5?\x00C\t'
        b'C\x0c\xc5?\x01C\tC\x0b\xc5?\x02C\tC\n'
        b'\xc5?\x03C\tC\t\xc5?\x04D\x07D\x08\xc4?'
        b'\x07C\x07C\x08\xc4?\x08C\x06D\x07\xc4?\nD'
        b'\x03D\x07\xc3?\x0cK\x06\xcf?\x02I\x07\xcf?\x04'
        b'E\t\xcf?\xff\xff\xe4'
    )
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

    def _draw(self, redraw=False):
        """Draw or lazily update the display.

        The updates are as lazy by default and avoid spending time redrawing
        if the time on display has not changed. However if redraw is set to
        True then a full redraw is be performed.
        """
        draw = wasp.watch.drawable
        hi = wasp.system.theme('bright')
        lo = wasp.system.theme('mid')

        if redraw:
            now = wasp.watch.rtc.get_localtime()

            # Clear the display and draw that static parts of the watch face
            draw.fill()
            #draw.blit(digits.clock_colon, 2*48, 80, fg=mid)

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

        # Draw the changeable parts of the watch face
        draw.blit(DIGITS[now[4] % 10], 40 + 1*90, 140, fg=hi)
        draw.blit(DIGITS[now[4] // 10], 40 + 0*90, 140, fg=hi)
        draw.blit(DIGITS[now[3] % 10], 40 + 1*90, 40, fg=lo)
        draw.blit(DIGITS[now[3] // 10], 40 + 0*90, 40, fg=lo)
        #draw.roundRect(25, 135, 180, 100, 5, lo)
        # Record the minute that is currently being displayed
        self._min = now[4]
