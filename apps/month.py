# SPDX-License-Identifier: MIT
# Copyright (C) 2023 Eloi Torrents
"""Month
~~~~~~~~~~~~

Simple calendar that displays months and highlights the current day.

Controls:
    - Swipe up to show next month.
    - Swipe down to show previous month.
    - Press the button to return to current month.

Icon courtesy of coffandro: https://github.com/coffandro

.. figure:: res/screenshots/MonthApp.png
    :width: 179
"""

import wasp
import icons
import fonts

MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
MLENGTH = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

def is_leap_year(year):
    return year % 400 == 0 or (year % 100 != 0 and year % 4 == 0)

def days_in_month(y, m):
    if m != 2:
        return MLENGTH[m - 1]
    if is_leap_year(int(y)):
        return 29
    return 28

# 2-bit RLE, 96x64, generated from res/icons/month_icon.png, 867 bytes
month_icon = (
    b'\x02'
    b'`@'
    b'\x1d\x87\x17\x87:\x81@\xebG\x81\x15\x81G\x818\x81'
    b'I\x81\x13\x81I\x816\x81K\x81\x11\x81K\x815\x81'
    b'K\x81\x11\x81K\x815\x81D\x83D\x81\x11\x81D\x83'
    b'D\x815\x81C\x81\x03\x81C\x81\x11\x81C\x81\x03\x81'
    b'C\x815\x81C\x81\x03\x81C\x81\x11\x81C\x81\x03\x81'
    b'C\x815\x81C\x81\x03\x81C\x81\x11\x81C\x81\x03\x81'
    b'C\x815\x81C\x81\x03\x81C\x81\x11\x81C\x81\x03\x81'
    b'C\x81/\x87C\x81\x03\x81C\x93C\x81\x03\x81C\x88'
    b'&\x82\x80\xb4\x86\xc0\xdb\xc1C\xc1\x03\xc1C\xc1\x91\xc1'
    b'C\xc1\x03\xc1C\xc1\x87\xc2#\xc1\x88\xc1C\xc1\x03\xc1'
    b'C\xc1\x91\xc1C\xc1\x03\xc1C\xc1\x89\xc1!\xc1\x89\xc1'
    b'C\xc1\x03\xc1C\xc1\x91\xc1C\xc1\x03\xc1C\xc1\x8a\xc1'
    b' \xc1\x89\xc1C\xc1\x03\xc1C\xc1\x91\xc1C\xc1\x03\xc1'
    b'C\xc1\x8a\xc1 \xc1\x89\xc1C\xc1\x03\xc1C\xc1\x91\xc1'
    b'C\xc1\x03\xc1C\xc1\x8a\xc1 \xc1\x89\xc1C\xc1\x03\xc1'
    b'C\xc1\x91\xc1C\xc1\x03\xc1C\xc1\x8a\xc1 \xc1\x89\xc1'
    b'D\xc3D\xc1\x91\xc1D\xc3D\xc1\x8a\xc1 \xc1\x89\xc1'
    b'K\xc1\x91\xc1K\xc1\x8a\xc1 \xc1\x8a\xc1I\xc1\x93\xc1'
    b'I\xc1\x8b\xc1 \xc1\x8b\xc1G\xc1\x95\xc1G\xc1\x8c\xc1'
    b' \xc1\x8c\xc7\x97\xc7\x8d\xc1 \xc1\xbe\xc1 \xff\x01 '
    b'\xc1@\xd7~\xc1 \xc1~\xc1 \xc1F\xcbB\xcbB'
    b'\xcbB\xcbF\xc1 \xc1F\xc1\t\xc1B\xc1\t\xc1B'
    b'\xc1\t\xc1B\xc1\t\xc1F\xc1 \xc1F\xc1\t\xc1B'
    b'\xc1\t\xc1B\xc1\t\xc1B\xc1\t\xc1F\xc1 \xc1F'
    b'\xc1\t\xc1B\xc1\t\xc1B\xc1\t\xc1B\xc1\t\xc1F'
    b'\xc1 \xc1F\xc1\t\xc1B\xc1\t\xc1B\xc1\t\xc1B'
    b'\xc1\t\xc1F\xc1 \xc1F\xc1\t\xc1B\xc1\t\xc1B'
    b'\xc1\t\xc1B\xc1\t\xc1F\xc1 \xc1F\xc1\t\xc1B'
    b'\xc1\t\xc1B\xc1\t\xc1B\xc1\t\xc1F\xc1 \xc1F'
    b'\xc1\t\xc1B\xc1\t\xc1B\xc1\t\xc1B\xc1\t\xc1F'
    b'\xc1 \xc1F\xcbB\xcbB\xcbB\xcbF\xc1 \xc1~'
    b'\xc1 \xc1~\xc1 \xc1F\xcbB\xcbB\xcbB\xcbF'
    b'\xc1 \xc1F\xc1\t\xc1B\xc1\t\xc1B\xc1\t\xc1B'
    b'\xc1\t\xc1F\xc1 \xc1F\xc1\t\xc1B\xc1\t\xc1B'
    b'\xc1\t\xc1B\xc1\t\xc1F\xc1 \xc1F\xc1\t\xc1B'
    b'\xc1\t\xc1B\xc1\t\xc1B\xc1\t\xc1F\xc1 \xc1F'
    b'\xc1\t\xc1B\xc1\t\xc1B\xc1\t\xc1B\xc1\t\xc1F'
    b'\xc1 \xc1F\xc1\t\xc1B\xc1\t\xc1B\xc1\t\xc1B'
    b'\xc1\t\xc1F\xc1 \xc1F\xc1\t\xc1B\xc1\t\xc1B'
    b'\xc1\t\xc1B\xc1\t\xc1F\xc1 \xc1F\xc1\t\xc1B'
    b'\xc1\t\xc1B\xc1\t\xc1B\xc1\t\xc1F\xc1 \xc1F'
    b'\xcbB\xcbB\xcbB\xcbF\xc1 \xc1~\xc1 \xc1~'
    b'\xc1 \xc1F\xcbB\xcbB\xcbB\xcbF\xc1 \xc1F'
    b'\xc1\t\xc1B\xc1\t\xc1B\xc1\t\xc1B\xc1\t\xc1F'
    b'\xc1 \xc1F\xc1\t\xc1B\xc1\t\xc1B\xc1\t\xc1B'
    b'\xc1\t\xc1F\xc1 \xc1F\xc1\t\xc1B\xc1\t\xc1B'
    b'\xc1\t\xc1B\xc1\t\xc1F\xc1 \xc1F\xc1\t\xc1B'
    b'\xc1\t\xc1B\xc1\t\xc1B\xc1\t\xc1F\xc1 \xc1F'
    b'\xc1\t\xc1B\xc1\t\xc1B\xc1\t\xc1B\xc1\t\xc1F'
    b'\xc1 \xc1F\xc1\t\xc1B\xc1\t\xc1B\xc1\t\xc1B'
    b'\xc1\t\xc1F\xc1 \xc1F\xc1\t\xc1B\xc1\t\xc1B'
    b'\xc1\t\xc1B\xc1\t\xc1F\xc1 \xc1F\xcbB\xcbB'
    b'\xcbB\xcbF\xc1 \xc1~\xc1 \xc1~\xc1 \xc1~'
    b'\xc1!\xc1|\xc1"\xc1|\xc1#\xc2x\xc2&\xf8\x14'
)

class MonthApp():
    """Monthly calenadar application.
    """
    NAME = 'Month'
    ICON = month_icon

    def __init__(self):
        self._reset()

    def _reset(self):
        now = wasp.watch.rtc.get_localtime()
        self._year = now[0]
        self._month = now[1]
        self._today =  now[2]
        self._start = (now[2] - now[6]) % 7 - 7

    def foreground(self):
        wasp.system.bar.clock = True
        self._draw()

        wasp.system.request_event(wasp.EventMask.SWIPE_UPDOWN)
        wasp.system.request_tick(15000)

    def swipe(self, event):
        if event[0] == wasp.EventType.UP:
            self._start = - ((-self._start + days_in_month(self._year, self._month)) % 7)
            self._month += 1
            if self._month == 12:
                self._month = 0
                self._year += 1
        elif event[0] == wasp.EventType.DOWN:
            self._start = (self._start  + days_in_month(self._year, (self._month - 1) % 12)) % 7 - 7
            self._month += -1
            if self._month == -1:
                self._month = 11
                self._year += -1
        self._draw()

    def press(self, button, state):
        if not state:
            return
        self._reset()
        self._draw()

    def tick(self, ticks):
        wasp.system.bar.update()

    def _draw(self, redraw=False):
        """Draw the display from scratch."""
        draw = wasp.watch.drawable
        hi = wasp.system.theme('bright')
        lo = draw.darken(wasp.system.theme('mid'), 2)

        if redraw:
            draw.reset()
            draw.fill(y=40)
        else:
            draw.fill()
        wasp.system.bar.draw()

        draw.set_font(fonts.sans24)
        draw.string(MONTHS[self._month - 1] + " " + str(self._year), 0, 50, width=240)

        # Gray
        draw.set_font(fonts.sans18)
        draw.set_color(lo)

        start = self._start - 1
        day = start 
        if day == -7:
            day = 0
        d_in_month = days_in_month(self._year, (self._month - 1) % 12) 
        d_prev_month = d_in_month
        for i in range(6*7):
            y_coord = 90 + 25 * (i//7)
            day += 1
            if day == 1:
                d_prev_month = 0
                d_in_month = days_in_month(self._year, self._month)
                draw.set_color(hi)
            if day == d_in_month + 1:
                draw.set_color(lo)
                day = 1
            day_str = str((day + d_prev_month - 1) % d_in_month +1)
            draw.string(day_str, 13 + 32*(i % 7),y_coord, width=20)
                       
        now = wasp.watch.rtc.get_localtime()
        if self._year == now[0] and self._month == now[1]:
            i = now[2] - self._start
            y_coord = 90 + 25 * (i//7)
            draw.set_color(hi, bg=0x64c8)
            draw.string(str(now[2]),13 + 32*(i % 7), y_coord, width=20)
            draw.set_color(0xFFFF)