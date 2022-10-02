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
        self._timer_reset()
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
        if not self._timer_started_at:
            self._reset()
        return True     # Request system default handling

    def press(self, button, state):
        if not state:
            return

        if self._timer_started:
            self._splits.insert(0, self._timer_count)
            del self._splits[9:]
            self._nsplits += 1
            wasp.watch.vibrator.pulse(duty=50, ms=50)
        else:
            self._reset()
            wasp.watch.vibrator.pulse(duty=50, ms=50)
        self._draw_splits()
        self._update()

    def touch(self, event):
        if self._timer_started:
            self._timer_stop()
            wasp.watch.vibrator.pulse(duty=50, ms=50)
        else:
            self._timer_start()
            wasp.watch.vibrator.pulse(duty=50, ms=250)
        self._update()
        self._draw_splits()

    def tick(self, ticks):
        self._update()

    def _reset(self):
        self._timer_reset()
        self._splits = []
        self._nsplits = 0

    def _draw_splits(self):
        draw = wasp.watch.drawable
        splits = self._splits
        if 0 == len(splits):
            draw.fill(0, 0, 60, 240, 180)
            return
        y = 240 - 6 - (len(splits) * 18)

        draw.set_font(fonts.sans18)
        draw.set_color(wasp.system.theme('mid'))

        n = self._nsplits
        for i, s in enumerate(splits):
            centisecs = s
            secs = centisecs // 100
            minutes = secs // 60
            hours = minutes // 60
            centisecs %= 100
            secs %= 60
            minutes %= 60
            if hours != 0:
                h = "{:02}h".format(hours)
            else:
                h = "   "
            if minutes != 0:
                m = "{:02}m".format(minutes)
            else:
                m = "   "

            t = '#{:02}  {}{}{:02}s{:02}cs'.format(n, h, m, secs, centisecs)
            n -= 1

            draw.string(t, 0, y + (i*18), 0, False)

    def _draw(self):
        """Draw the display from scratch."""
        draw = wasp.watch.drawable
        draw.fill()

        wasp.system.bar.draw()
        self._timer_draw()
        self._draw_splits()

    def _update(self):
        wasp.system.bar.update()
        self._timer_update()

    def _timer_start(self):
        uptime = wasp.watch.rtc.get_uptime_ms() // 10
        self._timer_started_at = uptime - self._timer_count

    def _timer_stop(self):
        self._timer_started_at = 0

    @property
    def _timer_started(self):
        return bool(self._timer_started_at)

    def _timer_reset(self):
        self._timer_count = 0
        self._timer_started_at = 0
        self._timer_last_count = -1

    def _timer_draw(self):
        self._timer_last_count = -1
        self._timer_update()

    def _timer_update(self):
        # Before we do anything else let's make sure count is
        # up to date
        if self._timer_started_at:
            uptime = wasp.watch.rtc.get_uptime_ms() // 10
            self._timer_count = uptime - self._timer_started_at
            if self._timer_count > 999*60*100:
                self._timer_reset()

        if self._timer_last_count != self._timer_count:
            centisecs = self._timer_count
            secs = centisecs // 100
            minutes = secs // 60
            hours = minutes // 60
            centisecs %= 100
            minutes %= 60
            secs %= 60
            if hours != 0:
                h = "{:02}h".format(hours)
            else:
                h = ""
            if minutes != 0:
                m = "{:02}m".format(minutes)
            else:
                m = ""

            t = '{}{}{:02}s  {}cs'.format(h, m, secs, centisecs)

            y = 35
            draw = wasp.watch.drawable
            draw.set_font(fonts.sans24)
            draw.set_color(draw.lighten(wasp.system.theme('ui'), wasp.system.theme('contrast')))
            draw.string(t, 0, y, 0, False)

            self._timer_last_count = self._timer_count

