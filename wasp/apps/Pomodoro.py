# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 Wolfgang Ginolas
"""Pomodoro Application
~~~~~~~~~~~~~~~~~~~~~~~

A pomodoro app, forked from timer.py.

    .. figure:: res/PomodApp.png
        :width: 179

        Screenshot of the Pomodoro Application

"""

import wasp
import fonts
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
_REPEAT_BUZZ = const(2)  # auto stop vibrating after _REPEAT_BUZZ vibrations
_REPEAT_MAX = const(99)  # auto stop repeat after 99 runs

_BUTTON_Y = const(200)

class PomodoroApp():
    """Allows the user to set a vibration alarm.
    """
    NAME = 'Pomod'
    ICON = icon

    def __init__(self):
        """Initialize the application."""
        self.minutes = widgets.Spinner(40, 60, 0, 99, 2)
        self.minutes2 = widgets.Spinner(140, 60, 0, 99, 2)
        self.current_alarm = None
        self.n_vibr = 0

        self.minutes.value = 15
        self.minutes2.value = 5
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

    def sleep(self):
        """doesn't exit when screen turns off"""
        return True

    def tick(self, ticks):
        """Notify the application that its periodic tick is due."""
        if self.state == _RINGING:
            wasp.watch.vibrator.pulse(duty=50, ms=950)
            wasp.system.keep_awake()

            self.n_vibr += 1
            if self.n_vibr % _REPEAT_BUZZ == 0:  # vibrated _REPEAT_BUZZ times
                # so no more repeat needed
                if self.n_vibr // _REPEAT_BUZZ < _REPEAT_MAX:  # restart another
                    self._start()
                else:  # stop from running for days
                    self._stop()
                    self.n_vibr = 0
        else:
            self._update()

    def touch(self, event):
        """Notify the application of a touchscreen touch event."""
        self.n_vibr = 0
        if self.state == _RINGING:
            mute = wasp.watch.display.mute
            mute(True)
            self._stop()
            mute(False)
        elif self.state == _RUNNING:
            if self.btn_stop.touch(event):
                self._stop()
            elif self.btn_add.touch(event):
                wasp.system.cancel_alarm(self.current_alarm, self._alert)
                self.current_alarm += 60
                wasp.system.set_alarm(self.current_alarm, self._alert)
                self._update()
        else:
            if self.minutes.touch(event) or self.minutes2.touch(event):
                pass
            elif self.btn_start.touch(event):
                self._start()

    def _start(self):
        self.state = _RUNNING
        now = wasp.watch.rtc.time()
        m = self.minutes.value if self.n_vibr // _REPEAT_BUZZ % 2 == 0 else self.minutes2.value

        # reduce by one second if repeating, to avoid growing offset
        self.current_alarm = now + max(m * 60 - _REPEAT_BUZZ, 1)
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
            draw.set_font(fonts.sans18)
            draw.string(self.NAME, 0, 150, width=240)
            draw.blit(icon, 73, 50)
        elif self.state == _RUNNING:
            self.btn_stop = widgets.Button(x=0, y=200, w=200, h=40, label="STOP")
            self.btn_stop.draw()
            self.btn_add = widgets.Button(x=200, y=200, w=40, h=40, label="+1")
            self.btn_add.draw()
            draw.reset()

            t = "Timer 1" if self.n_vibr // _REPEAT_BUZZ % 2 == 0 else "Timer 2"
            draw.set_font(fonts.sans18)
            n = self.n_vibr // _REPEAT_BUZZ
            t += " (#{})".format(n//2)
            draw.string(t, 10, 60)
            draw.set_font(fonts.sans28)
            draw.string(':', 110, 106, width=20)

            self._update()
            draw.set_font(fonts.sans18)
        else:  # _STOPPED
            draw.set_font(fonts.sans18)
            draw.string('T1', 56, 50)
            draw.string('T2', 156, 50)

            self.minutes.draw()
            self.minutes2.draw()

            self.btn_start = widgets.Button(x=20, y=200, w=200, h=40, label="START")
            self.btn_start.draw()
            draw.reset()

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
            draw.string(m, 50, 106, width=60)
            draw.string(s, 130, 106, width=60)

    def _alert(self):
        self.state = _RINGING
        wasp.system.wake()
        wasp.system.switch(self)
        self._draw()
