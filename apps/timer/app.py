# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 Wolfgang Ginolas
"""Timer Application
~~~~~~~~~~~~~~~~~~~~

An application to set a vibration in a specified amount of time. Like a kitchen timer.

    .. figure:: res/screenshots/TimerApp.png
        :width: 179

        Screenshot of the Timer Application

"""

import wasp
import fonts
import time
import widgets
import math
from micropython import const

# 2-bit RLE, generated from res/timer_icon.png, 345 bytes
icon = (
    b'\x02'
    b'`@'
    b'?\xff\r@\xb4I?\x14Q?\rW?\x08[?'
    b'\x04_?\x00c<Q\x80\xd0\x83Q:L\x87\x01\x87'
    b'L8K\x89\x01\x89K6J\x8b\x01\x8bJ4I\x8d'
    b'\x01\x8dI2I\x9dI0I\x83\x01\x97\x01\x83I.'
    b'H\x86\x01\x95\x01\x86H-H\xa3H,H\x92\x01\x92'
    b'H+G\x92\x03\x92G*G\x92\x05\x92G)G\x92'
    b"\x05\x92G(G\x82\x01\x8f\x07\x8f\x01\x82G'G\x83"
    b"\x01\x8e\x07\x8e\x01\x83G'F\x93\x07\x93F&G\x93"
    b'\x07\x93G%F\x94\x07\x94F%F\x94\x07\x94F%'
    b'F\x94\x07\x94F$G\x94\x07\x94G#G\x94\x07\x94'
    b'G#G\x94\x07\x94G#F\x95\x07\x95F#F\x81'
    b'\x04\x90\x07\x90\x04\x81F#F\x95\x07\x95F#G\x94'
    b'\x07\x94G#G\x94\x07\x94G#G\x94\x07\x94G$'
    b'F\x94\x07\x94F%F\x94\x07\x94F%F\x94\x07\x94'
    b"F%G\x93\x07\x93G%G\x93\x07\x93F'G\x83"
    b"\x01\x8e\x07\x8e\x01\x83G'G\x82\x01\x8f\x07\x8f\x01\x82"
    b'G(G\x92\x05\x92G)G\x93\x03\x93G*G\xa7'
    b'G+H\xa5H,G\xa5G-H\x86\x01\x9cH.'
    b'H\x84\x01\x96\x01\x85H0I\x9a\x01\x82I1J\x8d'
    b'\x01\x8dJ2K\x8b\x01\x8bK4K\x8a\x01\x89L5'
    b'N\x87\x01\x87N5S\x85S5k5k5k5'
    b'k5k5k\x1b'
)

_STOPPED = const(0)
_RUNNING = const(1)
_RINGING = const(2)

_BUTTON_Y = const(200)

class TimerApp():
    """Allows the user to set a vibration alarm.
    """
    NAME = 'Timer'
    ICON = icon

    def __init__(self):
        """Initialize the application."""
        self.minutes = widgets.Spinner(50, 60, 0, 99, 2)
        self.seconds = widgets.Spinner(130, 60, 0, 59, 2)
        self.current_alarm = None

        self.minutes.value = 10
        self.state = _STOPPED

    def foreground(self):
        """Activate the application."""
        self._draw()
        wasp.system.request_event(wasp.EventMask.TOUCH)
        wasp.system.request_tick(1000)

    def background(self):
        """De-activate the application."""
        if self.state == _RINGING:
            self.state = _STOPPED

    def tick(self, ticks):
        """Notify the application that its periodic tick is due."""
        if self.state == _RINGING:
            wasp.watch.vibrator.pulse(duty=50, ms=500)
            wasp.system.keep_awake()
        self._update()

    def touch(self, event):
        """Notify the application of a touchscreen touch event."""
        if self.state == _RINGING:
            mute = wasp.watch.display.mute
            mute(True)
            self._stop()
            mute(False)
        elif self.state == _RUNNING:
            self._stop()
        else:  # _STOPPED
            if self.minutes.touch(event) or self.seconds.touch(event):
                pass
            else:
                y = event[2]
                if y >= _BUTTON_Y:
                    self._start()


    def _start(self):
        self.state = _RUNNING
        now = wasp.watch.rtc.time()
        self.current_alarm = now + self.minutes.value * 60 + self.seconds.value
        wasp.system.set_alarm(self.current_alarm, self._alert)
        self._draw()

    def _stop(self):
        self.state = _STOPPED
        wasp.system.cancel_alarm(self.current_alarm, self._alert)
        self._draw()

    def _draw(self):
        """Draw the display from scratch."""
        draw = wasp.watch.drawable
        draw.fill()
        sbar = wasp.system.bar
        sbar.clock = True
        sbar.draw()

        if self.state == _RINGING:
            draw.set_font(fonts.sans24)
            draw.string(self.NAME, 0, 150, width=240)
            draw.blit(icon, 73, 50)
        elif self.state == _RUNNING:
            self._draw_stop(104, _BUTTON_Y)
            draw.string(':', 110, 120-14, width=20)
            self._update()
        else:  # _STOPPED
            draw.set_font(fonts.sans28)
            draw.string(':', 110, 120-14, width=20)

            self.minutes.draw()
            self.seconds.draw()

            self._draw_play(114, _BUTTON_Y)

    def _update(self):
        wasp.system.bar.update()
        draw = wasp.watch.drawable
        if self.state == _RUNNING:
            now = wasp.watch.rtc.time()
            s = self.current_alarm - now
            if s<0:
                s = 0
            m = str(math.floor(s // 60))
            s = str(math.floor(s) % 60)
            if len(m) < 2:
                m = '0' + m
            if len(s) < 2:
                s = '0' + s
            draw.set_font(fonts.sans28)
            draw.string(m, 50, 120-14, width=60)
            draw.string(s, 130, 120-14, width=60)

    def _draw_play(self, x, y):
        draw = wasp.watch.drawable
        for i in range(0,20):
            draw.fill(0xffff, x+i, y+i, 1, 40 - 2*i)

    def _draw_stop(self, x, y):
        wasp.watch.drawable.fill(0xffff, x, y, 40, 40)

    def _alert(self):
        self.state = _RINGING
        wasp.system.wake()
        wasp.system.switch(self)
