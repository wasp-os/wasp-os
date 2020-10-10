# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 Johannes Wache
"""Fibonacci clock

The Fibonacci sequence is a sequence of numbers created by the Italian
mathematician Fibonacci in the 13th century. This is a sequence starting with
1 and 1, where each subsequent number is the sum of the previous two. For the
clock I used the first 5 terms: 1, 1, 2, 3 and 5.

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
import icons

MONTH = 'JanFebMarAprMayJunJulAugSepOctNovDec'

# 2-bit RLE, generated from res/fibo_icon.png, 246 bytes
icon = (
    b'\x02'
    b'`@'
    b'?\xff\xffk\xd3\x01\xc9\x01@\x1er\x10\xd3\x01\xc9\x01'
    b'r\x10\xd3\x01\xc9\x01r\x10\xd3\x01\xc9\x01r\x10\xd3\x01'
    b'\xc9\x01r\x10\xd3\x01\xc9\x01r\x10\xd3\x01\xc9\x01r\x10'
    b'\xd3\x01\xc9\x01r\x10\xd3\x01\xc9\x01r\x10\xd3\x0br\x10'
    b'\xd3\x01I\x01r\x10\xd3\x01I\x01r\x10\xd3\x01I\x01'
    b'r\x10\xd3\x01I\x01r\x10\xd3\x01I\x01r\x10\xd3\x01'
    b'I\x01r\x10\xd3\x01I\x01r\x10\xd3\x01I\x01r\x10'
    b'\xd3\x01I\x01r.r\x10\xdd\x01r\x10\xdd\x01r\x10'
    b'\xdd\x01r\x10\xdd\x01r\x10\xdd\x01r\x10\xdd\x01r\x10'
    b'\xdd\x01r\x10\xdd\x01r\x10\xdd\x01r\x10\xdd\x01r\x10'
    b'\xdd\x01r\x10\xdd\x01r\x10\xdd\x01r\x10\xdd\x01r\x10'
    b'\xdd\x01r\x10\xdd\x01r\x10\xdd\x01r\x10\xdd\x01r\x10'
    b'\xdd\x01r\x10\xdd\x01r\x10\xdd\x01r\x10\xdd\x01r\x10'
    b'\xdd\x01r\x10\xdd\x01r\x10\xdd\x01r\x10\xdd\x01r\x10'
    b'\xdd\x01r\x10\xdd\x01r\x10\xdd\x01r\x10\xdd\x01r?'
    b'\xff\xffk'
)

class FibonacciClockApp():
    """Displays the time as a Fibonacci Clock
    """
    NAME = 'Fibo'
    ICON = icon

    def __init__(self):
        self.meter = wasp.widgets.BatteryMeter()
        self.notifier = wasp.widgets.StatusBar()
        self.fields = b'\x05\x03\x02\x01\x01'
        self.color_codes = [0xffff,0xf800,0x07e0,0x001f] # White, red, green and blue

    def foreground(self):
        """Activate the application."""
        self.on_screen = ( -1, -1, -1, -1, -1, -1 )
        self.draw()
        wasp.system.request_tick(1000)

    def sleep(self):
        return True

    def wake(self):
        self.update()

    def tick(self, ticks):
        self.update()

    def draw(self):
        """Redraw the display from scratch."""
        draw = wasp.watch.drawable

        draw.fill()
        self.on_screen = ( -1, -1, -1, -1, -1, -1 )
        self.update()
        self.meter.draw()

    def update(self):
        """Update the display (if needed).

        The updates are a lazy as possible and rely on an prior call to
        draw() to ensure the screen is suitably prepared.
        """
        now = wasp.watch.rtc.get_localtime()
        if now[3] == self.on_screen[3] and now[4] == self.on_screen[4]:
            if now[5] != self.on_screen[5]:
                self.meter.update()
                self.notifier.update()
                self.on_screen = now
            return False
        draw = wasp.watch.drawable

        #calculate colors of fields:
        field_colors = bytearray(5)
        hr = now[3]
        mn = now[4] // 5 # Clock can only display every 5 minutes
        if (hr >= 12):
            hr -= 12
        for i in range(5):
            if ((hr - self.fields[i]) >= 0):
                hr -= self.fields[i]
                field_colors[i] += 1

            if ((mn - self.fields[i]) >= 0):
                mn -= self.fields[i]
                field_colors[i] += 2

        draw.fill(x=71,y=60,w=23,h=23,bg=self.color_codes[field_colors[4]]) # 1 field
        draw.fill(x=71,y=85,w=23,h=23,bg=self.color_codes[field_colors[3]]) # 1 field
        draw.fill(x=21,y=60,w=48,h=48,bg=self.color_codes[field_colors[2]]) # 2 field
        draw.fill(x=21,y=110,w=73,h=73,bg=self.color_codes[field_colors[1]]) # 3 field
        draw.fill(x=96,y=60,w=123,h=123,bg=self.color_codes[field_colors[0]]) # 5 field

        self.on_screen = now

        month = now[1] - 1
        month = MONTH[month*3:(month+1)*3]
        draw.string('{} {} {}'.format(now[2], month, now[0]),
                0, 202, width=240)

        self.meter.update()
        self.notifier.update()
        return True
