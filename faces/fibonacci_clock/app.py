# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 Johannes Wache

"""Fibonacci clock
~~~~~~~~~~~~~~~~~~

The Fibonacci sequence is a sequence of numbers created by the Italian
mathematician Fibonacci in the 13th century. This is a sequence starting with
1 and 1, where each subsequent number is the sum of the previous two. For the
clock I used the first 5 terms: 1, 1, 2, 3 and 5.

    .. figure:: res/screenshots/FibonacciClockApp.png
        :width: 179

        Screenshot of the fibonacci clock application

The screen of the clock is made up of five squares whose side lengths match
the first five Fibonacci numbers: 1, 1, 2, 3 and 5. The hours are displayed
using red and the minutes using green. When a square is used to display both
the hours and minutes it turns blue. White squares are ignored.

To tell time on the Fibonacci clock you need to do some calculations. To read
the hour, simply add up the corresponding values of the red and blue squares.
To read the minutes, do the same with the green and blue squares. The minutes
are displayed in 5 minute increments (0 to 12) so you have to multiply your
result by 5 to get the actual number.
"""

import wasp

COLORS = [0xffff,0xf800,0x07e0,0x001f] # White, red, green and blue
FIELDS = b'\x05\x03\x02\x01\x01'
MONTH = 'JanFebMarAprMayJunJulAugSepOctNovDec'

class FibonacciClockApp():
    """Displays the time as a Fibonacci Clock.
    """
    NAME = 'Fibo'

    def foreground(self):
        """Activate the application."""
        wasp.system.bar.clock = False
        self._draw(True)
        wasp.system.request_tick(1000)

    def sleep(self):
        return True

    def wake(self):
        self._draw()

    def tick(self, ticks):
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
            if not now or self._min == now[4]:
                return

        #calculate colors of fields:
        field_colors = bytearray(5)
        hr = now[3]
        mn = now[4] // 5 # Clock can only display every 5 minutes
        if (hr >= 12):
            hr -= 12
        for i in range(5):
            if ((hr - FIELDS[i]) >= 0):
                hr -= FIELDS[i]
                field_colors[i] += 1

            if ((mn - FIELDS[i]) >= 0):
                mn -= FIELDS[i]
                field_colors[i] += 2

        draw.fill(x=71,y=60,w=23,h=23,bg=COLORS[field_colors[4]]) # 1 field
        draw.fill(x=71,y=85,w=23,h=23,bg=COLORS[field_colors[3]]) # 1 field
        draw.fill(x=21,y=60,w=48,h=48,bg=COLORS[field_colors[2]]) # 2 field
        draw.fill(x=21,y=110,w=73,h=73,bg=COLORS[field_colors[1]]) # 3 field
        draw.fill(x=96,y=60,w=123,h=123,bg=COLORS[field_colors[0]]) # 5 field

        month = now[1] - 1
        month = MONTH[month*3:(month+1)*3]
        draw.string('{} {} {}'.format(now[2], month, now[0]),
                0, 202, width=240)

        # Record the minute that is currently being displayed
        self._min = now[4]
