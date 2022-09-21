# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 Daniel Thompson

"""Stopwatch
~~~~~~~~~~~~

Simple stop/start watch with support for split times.

.. figure:: res/StopclockApp.png
    :width: 179
"""
import wasp
import icons
import fonts

class StopwatchApp():
    """Stopwatch application."""
    # Stopwatch requires too many pixels to fit into the launcher

    NAME = 'Stopclock'
    ICON = icons.app

    def __init__(self):
        self._timer = Stopwatch(120-36)
        self._reset()

    def foreground(self):
        """Activate the application."""
        wasp.system.bar.clock = True
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
        if not self._timer._started_at:
            self._reset()
        return True     # Request system default handling

    def press(self, button, state):
        if not state:
            return

        if self._timer.started:
            self._timer.stop()
        else:
            self._timer.start()

    def touch(self, event):
        if self._timer.started:
            self._splits.insert(0, self._timer.count)
            del self._splits[4:]
            self._nsplits += 1
        else:
            self._reset()

        self._update()
        self._draw_splits()

    def tick(self, ticks):
        self._update()

    def _reset(self):
        self._timer.reset()
        self._splits = []
        self._nsplits = 0

    def _draw_splits(self):
        draw = wasp.watch.drawable
        splits = self._splits
        if 0 == len(splits):
            draw.fill(0, 0, 120, 240, 120)
            return
        y = 240 - 6 - (len(splits) * 24)

        draw.set_font(fonts.sans24)
        draw.set_color(wasp.system.theme('mid'))

        n = self._nsplits
        for i, s in enumerate(splits):
            centisecs = s
            secs = centisecs // 100
            centisecs %= 100
            minutes = secs // 60
            secs %= 60

            t = '# {}   {:02}:{:02}.{:02}'.format(n, minutes, secs, centisecs)
            n -= 1

            w = fonts.width(fonts.sans24, t)
            draw.string(t, 0, y + (i*24), 240)

    def _draw(self):
        """Draw the display from scratch."""
        draw = wasp.watch.drawable
        draw.fill()

        wasp.system.bar.draw()
        self._timer.draw()
        self._draw_splits()

    def _update(self):
        wasp.system.bar.update()
        self._timer.update()

class Stopwatch:
    """A stopwatch widget"""
    def __init__(self, y):
        self._y = y
        self.reset()

    def start(self):
        uptime = wasp.watch.rtc.get_uptime_ms() // 10
        self._started_at = uptime - self.count

    def stop(self):
        self._started_at = 0

    @property
    def started(self):
        return bool(self._started_at)

    def reset(self):
        self.count = 0
        self._started_at = 0
        self._last_count = -1

    def draw(self):
        self._last_count = -1
        self.update()

    def update(self):
        # Before we do anything else let's make sure count is
        # up to date
        if self._started_at:
            uptime = wasp.watch.rtc.get_uptime_ms() // 10
            self.count = uptime - self._started_at
            if self.count > 999*60*100:
                self.reset()

        if self._last_count != self.count:
            centisecs = self.count
            secs = centisecs // 100
            centisecs %= 100
            minutes = secs // 60
            secs %= 60

            t1 = '{}:{:02}'.format(minutes, secs)
            t2 = '{:02}'.format(centisecs)

            y = self._y
            draw = wasp.watch.drawable
            draw.set_font(fonts.sans36)
            draw.set_color(draw.lighten(wasp.system.theme('ui'), wasp.system.theme('contrast')))
            w = fonts.width(fonts.sans36, t1)
            draw.string(t1, 180-w, y)
            draw.fill(0, 0, y, 180-w, 36)
            draw.set_font(fonts.sans24)
            draw.string(t2, 180, y+18, width=46)

            self._last_count = self.count
