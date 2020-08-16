# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 Daniel Thompson

import wasp
import icons
import fonts

class StopwatchApp():
    """Stopwatch application.

    .. figure:: res/TimerApp.png
        :width: 179

        Screenshot of the stopwatch application
    """
    NAME = 'Timer'
    ICON = icons.app

    def __init__(self):
        self._meter = wasp.widgets.BatteryMeter()
        self._reset()
        self._count = 0

    def foreground(self):
        """Activate the application."""
        self._last_clock = ( -1, -1, -1, -1, -1, -1 )

        self._draw()
        wasp.system.request_tick(97)
        wasp.system.request_event(wasp.EventMask.TOUCH |
                                  wasp.EventMask.BUTTON |
                                  wasp.EventMask.NEXT)

    def sleep(self):
        return True

    def wake(self):
        self._update()

    def swipe(self, event):
        """Handle NEXT events by augmenting the default processing by resetting
        the count if we are not currently timing something.

        No other swipe event is possible for this application.
        """
        if not self._started_at:
            self._reset()
        return True     # Request system default handling

    def press(self, button, state):
        if not state:
            return

        if self._started_at:
            self._update()
            self._started_at = 0
        else:
            uptime = wasp.watch.rtc.get_uptime_ms()
            uptime //= 10
            self._started_at = uptime - self._count
            self._update()

    def touch(self, event):
        if self._started_at:
            self._update()
            self._splits.insert(0, self._count)
            del self._splits[4:]
            self._nsplits += 1
        else:
            self._reset()
            self._update()

        self._draw_splits()

    def tick(self, ticks):
        self._update()

    def _reset(self):
        self._started_at = 0
        self._count = 0
        self._last_count = -1
        self._splits = []
        self._nsplits = 0

    def _draw_splits(self):
        draw = wasp.watch.drawable
        splits = self._splits
        if 0 == len(splits):
            draw.fill(0, 0, 120, 240, 120)
            return
        y = 240 - 6 - (len(splits) * 24)
        
        n = self._nsplits
        for i, s in enumerate(splits):
            centisecs = s
            secs = centisecs // 100
            centisecs %= 100
            minutes = secs // 60
            secs %= 60

            t = '# {}   {:02}:{:02}.{:02}'.format(n, minutes, secs, centisecs)
            n -= 1

            draw.set_font(fonts.sans24)
            draw.set_color(0xe73c)
            w = fonts.width(fonts.sans24, t)
            draw.string(t, 0, y + (i*24), 240)

    def _draw(self):
        """Draw the display from scratch."""
        draw = wasp.watch.drawable
        draw.fill()

        self._last_count = -1
        self._update()
        self._meter.draw()
        self._draw_splits()

    def _update(self):
        # Before we do anything else let's make sure _count is
        # up to date
        if self._started_at:
            uptime = wasp.watch.rtc.get_uptime_ms()
            uptime //= 10
            self._count = uptime - self._started_at
            if self._count > 999*60*100:
                self._reset()

        draw = wasp.watch.drawable

        # Lazy update of the clock and battery meter
        now = wasp.watch.rtc.get_localtime()
        if now[4] != self._last_clock[4]:
            t1 = '{:02}:{:02}'.format(now[3], now[4])
            draw.set_font(fonts.sans28)
            draw.set_color(0xe73c)
            draw.string(t1, 48, 12, 240-96)
            self._last_clock = now
            self._meter.update()

        if self._last_count != self._count:
            centisecs = self._count
            secs = centisecs // 100
            centisecs %= 100
            minutes = secs // 60
            secs %= 60

            t1 = '{}:{:02}'.format(minutes, secs)
            t2 = '{:02}'.format(centisecs)

            draw.set_font(fonts.sans36)
            draw.set_color(0xc67f)
            w = fonts.width(fonts.sans36, t1)
            draw.string(t1, 180-w, 120-36)
            draw.fill(0, 0, 120-36, 180-w, 36)

            draw.set_font(fonts.sans24)
            draw.string(t2, 180, 120-36+18, width=46)
            self._last_count = self._count
