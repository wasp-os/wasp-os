# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2022 github user thiswillbeyourgithub
"""Pomodoro Application
~~~~~~~~~~~~~~~~~~~~~~~

A pomodoro app, forked from timer.py. Swipe laterally to load presets and vertically
to change number of vibration. Vibration pattern are randomized if vibrating
more than 4 times.

    .. figure:: res/PomodApp.png
        :width: 179

        Screenshot of the Pomodoro Application

"""

import wasp
import fonts
import widgets
import math
import random
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
_REPEAT_MAX = const(99)  # auto stop repeat after 99 runs
_FIELDS = const(1234567890)
_MAX_VIB = const(15)  # max number of second the watch you vibrate

# you can add your own presets here:
_PRESETS = ['15,4', '10,3', '20,5']


class PomodoroApp():
    """Allows the user to set a periodic vibration alarm, Pomodoro style."""
    NAME = 'Pomod'
    ICON = icon

    def __init__(self):
        self.current_alarm = None
        self.nb_vibrat_total = 0  # number of time it vibrated
        self.nb_vibrat_per_alarm = 10  # number of times to vibrate each time

        self.last_preset = 0
        self.queue = _PRESETS[0]
        self.last_run = -1
        self.state = _STOPPED

    def foreground(self):
        self._draw()
        wasp.system.request_event(wasp.EventMask.TOUCH |
                                  wasp.EventMask.SWIPE_LEFTRIGHT |
                                  wasp.EventMask.SWIPE_UPDOWN)
        wasp.system.request_tick(1000)

    def background(self):
        if self.state == _RINGING:
            self._start()
        elif self.state == _STOPPED:
            self.__init__()

    def sleep(self):
        """don't exit when screen turns off"""
        return True

    def tick(self, ticks):
        if self.state == _RINGING:
            if self.nb_vibrat_per_alarm <= 3:
                wasp.watch.vibrator.pulse(duty=50, ms=650)
            else:
                wasp.watch.time.sleep(random.randint(0, 150) * 0.001)  # offset pattern
                if random.random() > 0.8:  # one very long vibration
                    wasp.watch.vibrator.pulse(duty=random.randint(20, 60), ms=1000)
                elif random.random() > 0.66:  # one long vibration
                    wasp.watch.vibrator.pulse(duty=random.randint(20, 60),
                                              ms=random.randint(750, 850))
                else:  # burst of vibration
                    wasp.watch.vibrator.pulse(duty=20, ms=random.randint(100, 200))
                    wasp.watch.time.sleep(random.randint(50, 150) * 0.001)
                    wasp.watch.vibrator.pulse(duty=20, ms=random.randint(100, 200))
                    wasp.watch.time.sleep(random.randint(50, 150) * 0.001)
                    wasp.watch.vibrator.pulse(duty=20, ms=random.randint(100, 200))
            wasp.system.keep_awake()
            self.nb_vibrat_total += 1
            if self.nb_vibrat_total % self.nb_vibrat_per_alarm == 0:
                # vibrated self.nb_vibrat_per_alarm times so
                # no more repeat needed
                if self.nb_vibrat_total // self.nb_vibrat_per_alarm // len(self.squeue) < _REPEAT_MAX:
                    # restart another
                    self._start()
                else:  # avoid running for days if forgotten
                    self._stop()

        else:
            self._update()

    def swipe(self, event):
        if self.state == _STOPPED:
            draw = wasp.watch.drawable
            draw.set_font(fonts.sans24)
            if event[0] == wasp.EventType.UP:
                self.nb_vibrat_per_alarm = max(1, (self.nb_vibrat_per_alarm + 1) % _MAX_VIB)
            elif event[0] == wasp.EventType.DOWN:
                self.nb_vibrat_per_alarm -= 1
                if self.nb_vibrat_per_alarm == 0:
                    self.nb_vibrat_per_alarm = _MAX_VIB
            else:
                if event[0] == wasp.EventType.RIGHT:
                    self.last_preset += 1
                elif event[0] == wasp.EventType.LEFT:
                    self.last_preset -= 1
                self.last_preset %= len(_PRESETS)
                self.queue = _PRESETS[self.last_preset]
            draw.string(self.queue, 0, 35, right=True, width=240)
            draw.string("V{}".format(self.nb_vibrat_per_alarm), 0, 35)

    def touch(self, event):
        if self.state == _RINGING:
            mute = wasp.watch.display.mute
            mute(False)
        elif self.state == _RUNNING:
            if self.btn_stop.touch(event):
                self._stop()
            elif self.btn_add.touch(event):
                wasp.system.cancel_alarm(self.current_alarm, self._alert)
                self.current_alarm += 60
                wasp.system.set_alarm(self.current_alarm, self._alert)
                wasp.watch.vibrator.pulse(duty=25, ms=50)
                self._update()
        elif self.state == _STOPPED:
            if self.btn_del.touch(event):
                if len(self.queue) > 1:
                    self.queue = self.queue[:-1]
                else:
                    self.queue = ""
            elif self.btn_start.touch(event):
                if self.queue != "" and not self.queue.endswith(","):
                    self.squeue = [int(x) for x in self.queue.split(",")]
                    self._start(first_run=True)
                    return
            elif len(self.queue) < 13:
                if self.btn_add.touch(event):
                    if len(self.queue) >= 1 and self.queue[-1] != ",":
                        self.queue += ","
                else:
                    for i, b in enumerate(self.btns):
                        if b.touch(event):
                            self.queue += str((i + 1) % 10)
                            break
            draw = wasp.watch.drawable
            draw.set_font(fonts.sans24)
            draw.string(self.queue, 0, 35, right=True, width=240)
            draw.string("V{}".format(self.nb_vibrat_per_alarm), 0, 35)

    def _start(self, first_run=False):
        if self.btns is not None:  # save some memory
            for b in self.btns:
                b = None
                del b
            self.btns = None
        wasp.gc.collect()

        self.state = _RUNNING
        now = wasp.watch.rtc.time()
        self.last_run += 1
        if self.last_run >= len(self.squeue):
            self.last_run = 0
        m = self.squeue[self.last_run]

        # reduce by one second if repeating, to avoid growing offset
        if first_run:
            self.current_alarm = now + max(m * 60, 1)
        else:
            self.current_alarm = now + max(m * 60 - self.nb_vibrat_per_alarm, 1)
        wasp.system.set_alarm(self.current_alarm, self._alert)
        self._draw()

    def _stop(self):
        self.state = _STOPPED
        wasp.system.cancel_alarm(self.current_alarm, self._alert)
        self.last_run = -1
        self.nb_vibrat_total = 0
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
            self.btn_stop = widgets.Button(x=0, y=200, w=160, h=40,
                                           label="STOP")
            self.btn_stop.draw()
            self.btn_add = widgets.Button(x=160, y=200, w=80, h=40,
                                          label="+1")
            self.btn_add.draw()
            draw.reset()
            t = "Timer #{}/{}  ({})".format(self.last_run + 1,
                                            len(self.squeue),
                                            self.nb_vibrat_total // self.nb_vibrat_per_alarm // len(self.squeue))
            draw.string(t, 10, 60)
            draw.set_font(fonts.sans28)
            draw.string(':', 110, 106, width=20)

            self._update()
            draw.set_font(fonts.sans18)
        elif self.state == _STOPPED:
            self.btns = []
            fields = str(_FIELDS)
            for y in range(2):
                for x in range(5):
                    btn = widgets.Button(x=x*48,
                                         y=y*65+60,
                                         w=49,
                                         h=59,
                                         label=fields[x + 5*y])
                    btn.draw()
                    self.btns.append(btn)
            self.btn_del = widgets.Button(x=0,
                                          y=190,
                                          w=76,
                                          h=50,
                                          label="Del.")
            self.btn_del.draw()
            self.btn_add = widgets.Button(x=80,
                                          y=190,
                                          w=76,
                                          h=50,
                                          label="Then")
            self.btn_add.draw()
            self.btn_start = widgets.Button(x=160,
                                            y=190,
                                            w=80,
                                            h=50,
                                            label="Go")
            self.btn_start.update(txt=0, frame=wasp.system.theme('mid'),
                                  bg=0xf800)
            draw.reset()
            draw.set_font(fonts.sans24)
            draw.string(self.queue, 0, 35, right=True, width=240)
            draw.string("V{}".format(self.nb_vibrat_per_alarm), 0, 35)

    def _update(self):
        wasp.system.bar.update()
        draw = wasp.watch.drawable
        if self.state == _RUNNING:
            now = wasp.watch.rtc.time()
            s = max(self.current_alarm - now, 0)
            m = math.floor(s // 60)
            s = math.floor(s) % 60
            if len(str(m)) > 5:
                prefix = "+"
                m = int(str(m)[-4:])
            else:
                prefix = ""
            draw.set_font(fonts.sans28)
            draw.string("{}{:02d}:{:02d}".format(prefix, m, s), 90, 106,
                        width=60)

    def _alert(self):
        self.state = _RINGING
        wasp.system.wake()
        wasp.system.switch(self)
        self._draw()
