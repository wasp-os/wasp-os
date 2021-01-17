# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 Daniel Thompson

"""Step counter
~~~~~~~~~~~~~~~

Provide a daily step count.

    .. figure:: res/StepsApp.png
        :width: 179

The step counts automatically reset at midnight.
"""

import wasp

import array
import datetime
import fonts
import icons
import time
import watch

# 2-bit RLE, generated from res/feet.png, 240 bytes
feet = (
    b'\x02'
    b'00'
    b'\x13\xc1-\xc4+\xc6*\xc6*\xc6&\xc3\x01\xc6\t\xc2'
    b'\x1b\xc3\x02\xc5\x08\xc4\x1a\xc4\x01\xc5\x08\xc5\x19\xc4\x02\xc3'
    b'\x08\xc6\x17\xc1\x02\xc3\x02\xc3\x08\xc6\x16\xc3\x02\xc1\x0e\xc6'
    b'\x01\xc3\x12\xc3\x11\xc6\x01\xc3\x13\xc2\x05\xc2\n\xc5\x02\xc3'
    b'\x10\xc2\x01\xc2\x02\xc6\n\xc4\x01\xc4\x10\xc2\x04\xc7\x0b\xc1'
    b'\x03\xc3\x11\xc3\x02\xc8\x10\xc2\x01\xc3\r\xc2\x02\xc9\x13\xc3'
    b'\x0b\xc1\x05\xc9\x0c\xc2\x05\xc3\x0b\xc2\x03\xc9\x0c\xc5\x03\xc2'
    b'\x0c\xc2\x02\xca\x0c\xc6\x05\xc2\t\xc2\x02\xca\x0c\xc7\x03\xc3'
    b'\r\xca\x0c\xc8\x02\xc3\x0c\xca\r\xc9\x02\xc1\r\xca\r\xc9'
    b'\x04\xc2\n\xca\x0e\xc9\x02\xc3\n\xca\x0e\xc9\x02\xc2\x0b\xca'
    b'\x0e\xca\x0e\xca\x0e\xca\x0f\xc9\x0e\xca\x0f\xca\r\xca\x0f\xca'
    b'\r\xca\x10\xcb\x0b\xca\x10\xcc\n\xca\x10\xcd\t\xca\x11\xcc'
    b'\x08\xca\x12\xcc\x07\xcb\x13\xcb\x06\xcb\x14\xcb\x05\xcc\x15\xca'
    b'\x04\xcc\x16\xc9\x05\xcc\x17\xc7\x05\xcd\x17\xc7\x05\xcc\x1a\xc4'
    b"\x07\xcb%\xca&\xca'\xc8)\xc6+\xc4\x0e"
)

class StepCounterApp():
    """Step counter application."""
    NAME = 'Steps'
    ICON = icons.app

    def __init__(self):
        watch.accel.reset()
        self._count = 0
        self._wake = 0
        self.prev_days  = array.array("i", (-1,)*7)
        self.prev_steps = array.array("i", (-1,)*7)
        # page 0 is the 'main' page that only shows todays step count
        # page 7 is a special page informing no previous times exist
        self.page = 0
        

    def foreground(self):
        """Cancel the alarm and draw the application.

        Cancelling the alarm has two effects. Firstly it ensures the
        step count won't change whilst we are watching it and, secondly
        it ensures that if the time of day has been set to a value in
        the past that we reconfigure the alarm.

        This does in the side effect that if the application of open at
        midnight then the reset doesn't happen for that day.
        """
        wasp.system.request_event(wasp.EventMask.SWIPE_UPDOWN)
        wasp.system.cancel_alarm(self._wake, self._reset)
        wasp.system.bar.clock = True
        self._draw()
        wasp.system.request_tick(1000)

    def swipe(self, event):
        """swipe between main view and previous step counts"""
        today = datetime.date.today()
        weekday = today.weekday()

        # find the earliest record and last page
        start_idx = weekday
        idx = start_idx
        last_page = 0
        found = False
        while not found:
            print(idx)
            next_idx = idx - 1 if idx > 0 else 6
            if self.prev_steps[next_idx] == -1 or next_idx == start_idx:
                found = True
            else:
                last_page += 1
                idx = next_idx

        if event[0] == wasp.EventType.UP and self.page != 0 and self.page != 8: 
            # Cycle forward to next page
            self.page -= 1
        elif event[0] == wasp.EventType.UP and self.page == 8:
            # Cycle back to last page
            self.page = last_page
        elif event[0] == wasp.EventType.DOWN:
            # Cycle back to prev day's stepcount
            if self.page != last_page:
                self.page += 1
            else:
                self.page = 8

        self._draw()

    def background(self):
        """Set an alarm to trigger at midnight and reset the counter."""
        now = watch.rtc.get_localtime()
        yyyy = now[0]
        mm = now[1]
        dd = now[2]
        then = (yyyy, mm, dd+1, 0, 0, 0, 0, 0, 0)

        self._wake = time.mktime(then)
        wasp.system.set_alarm(self._wake, self._reset)

    def _reset(self):
        """"Reset the step counter and re-arm the alarm."""
        today = datetime.date.today()
        weekday = today.weekday()
        self.prev_steps[weekday] = watch.accel.steps
        # Pack the date into an int
        self.prev_days[weekday] = today.year << 8*2 | today.month << 8 | today.day
        watch.accel.steps = 0
        self._wake += 24 * 60 * 60
        wasp.system.set_alarm(self._wake, self._reset)

    def tick(self, ticks):
        self._count += 686;
        self._update()

    def _draw(self):
        """Draw the display from scratch."""
        draw = wasp.watch.drawable
        draw.fill()

        if self.page == 0:
            draw.blit(feet, 12, 132-24)
        else:
            draw.blit(feet, 12, 180)

        self._update()
        wasp.system.bar.draw()

    def _draw_current_steps(self, draw):
        # Update the step count
        count = watch.accel.steps
        t = str(count)
        w = fonts.width(fonts.sans36, t)
        draw.set_font(fonts.sans36)
        draw.set_color(draw.lighten(wasp.system.theme('spot1'), wasp.system.theme('contrast')))
        if self.page == 0:
            draw.string(t, 228-w, 132-18)
        else:
            draw.string(t, 228-w, 180)

    def _draw_page(self, draw):
        draw.set_color(wasp.system.theme("bright"))
        if self.page == 8:
            t1 = "No earlier step"
            t2 = "counts available"
            w1 = fonts.width(fonts.sans24, t1)
            w2 = fonts.width(fonts.sans24, t2)
            draw.set_font(fonts.sans24)
            draw.string(t1, 0, 132-24, draw._display.width)
            draw.string(t2, 0, 132, draw._display.width)
        elif self.page != 0:
            today = datetime.date.today()
            weekday = today.weekday()
            idx = weekday - self.page
            if idx < 0:
                idx += 7
            day = datetime.date(
                    year = (self.prev_days[idx] & 0xFFFF0000) >> 8*2,
                    month = (self.prev_days[idx] & 0xFF00) >> 8,
                    day = (self.prev_days[idx] & 0xFF))
            t1 = day.strftime("%b %-d, %Y")
            t2 = str(self.prev_steps[idx])
            w1 = fonts.width(fonts.sans24, t1)
            w2 = fonts.width(fonts.sans36, t2)
            draw.set_font(fonts.sans24)
            draw.string(t1, 0, 112-38, draw._display.width)
            draw.set_font(fonts.sans36)
            draw.string(t2, 0, 112, draw._display.width)


    def _update(self):
        draw = wasp.watch.drawable

        # Update the status bar
        now = wasp.system.bar.update()
        self._draw_page(draw)
        self._draw_current_steps(draw)

        
