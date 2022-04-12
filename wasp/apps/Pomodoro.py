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

# 2-bit RLE, 96x64, generated from png provided by plan5, 239 bytes
icon = (
    b'\x02'
    b'`@'
    b'?\xb1@\x1eD?\x1bE?\x1bE?\x1dC?"'
    b'\x80\xb4\x82?\x11C\x01\x83\x05B\x86?\x0cI\x03C'
    b'\x89?\x0bF\x05C\xc0\xd2\xc1\x89?\x15D\x8a?\x00'
    b'\x82\x0c\x82\x04C\x01\x8b<\x84\x08\x85\n\x8a:\x92\x05'
    b'\x83\x03\x8a8\x93\x03\x88\x01\x8a6\x93\x03\x954\x94\x02'
    b'\x972\x95\x01\x990\xb1/\xb1.\xa7\x01\x8b-\xa5\x03'
    b'\x8b,\xa4\x04\x8d+\xa1\x06\x8e*\xa0\x07\x90)\x9e\x08'
    b'\x91)\x9b\x0b\x91)\x99\x0c\x92)\x98\x0c\x93(\x99\x0b'
    b"\x95'\x98\x03\x84\x04\x96'\x98\x03\x84\x03\x97'\x98\x03"
    b"\x84\x03\x97'\x99\x02\x84\x02\x82\x01\x95'\x9a\x05\x83\x02"
    b'\x95(\x9a\x03\x83\x04\x93)\xa0\x05\x92)\xa1\x04\x92)'
    b'\xa2\x04\x91)\xa4\x03\x90*\xa4\x03\x8e+\xa5\x02\x8e,'
    b'\xa6\x01\x8c-\xa7\x01\x8b.\xb1/\xb10\xaf2\xad4'
    b'\xab6\xa98\xa7:\xa5<\xa3?\x00\x9f?\x04\x9b?'
    b'\x08\x97?\r\x91?\x14\x89?\xff\xff/'
)

_STOPPED = const(0)
_RUNNING = const(1)
_RINGING = const(2)
_REPEAT_BUZZ = const(2)  # auto stop vibrating after _REPEAT_BUZZ vibrations
_REPEAT_MAX = const(999)  # auto stop repeat after 999 runs


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
            self.btn_add = widgets.Button(x=180, y=200, w=60, h=40, label="+1")
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
