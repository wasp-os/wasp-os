# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 Daniel Thompson

"""Sports timer
~~~~~~~~~~~~~~~

A combined stopwatch and step counter.

.. figure:: res/screenshots/SportsApp.png
    :width: 179
"""
import wasp
import icons
import fonts

class SportsApp():
    """Sports timer application."""
    NAME = 'Sports'
    ICON = icons.app

    def __init__(self):
        self._timer = wasp.widgets.Stopwatch(120-36)
        self._reset()

    def foreground(self):
        """Activate the application."""
        wasp.system.bar.clock = True
        self._draw()
        wasp.system.request_tick(97)
        wasp.system.request_event(wasp.EventMask.TOUCH | wasp.EventMask.BUTTON)

    def background(self):
        if not self._timer.started:
            self._timer.reset()

    def sleep(self):
        return True

    def wake(self):
        self._update()

    def press(self, button, state):
        if not state:
            return

        steps = wasp.watch.accel.steps

        if self._timer.started:
            self._timer.stop()
        else:
            self._timer.start()
            self._last_steps = steps

    def touch(self, event):
        if not self._timer.started:
            self._reset()
            self._update()

    def tick(self, ticks):
        self._update()

    def _reset(self):
        self._timer.reset()
        self._steps = 0
        self._last_steps = 0

    def _draw(self):
        """Draw the display from scratch."""
        draw = wasp.watch.drawable
        draw.fill()

        wasp.system.bar.draw()
        self._timer.draw()

    def _update(self):
        wasp.system.bar.update()
        self._timer.update()

        if self._timer.started:
            steps = wasp.watch.accel.steps
            redraw = bool(steps - self._last_steps)
            self._steps += steps - self._last_steps
            self._last_steps = steps
        else:
            redraw = True

        if redraw:
            draw = wasp.watch.drawable
            draw.set_font(fonts.sans36)
            draw.set_color(draw.lighten(wasp.system.theme('spot1'), wasp.system.theme('contrast')))
            draw.string(str(self._steps), 0, 170, 228, True)
