# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2022 github user thiswillbeyourgithub
"""Pomodoro Application
~~~~~~~~~~~~~~~~~~~~~~~

A pomodoro app, forked from timer.py. Swipe laterally to load presets and vertically
to change number of vibration. Vibration patterns are randomized if vibrating
more than 4 times to make sure you notice.

.. figure:: res/screenshots/PomodoroApp.png
    :width: 179
"""

import wasp
import fonts
import widgets
import math
import random
from micropython import const

# 2-bit RLE, 57x56, generated from png provided by plan5, 211 bytes
icon = (
    b'\x02'
    b'98'
    b'\x1d@\x1eD3E3E5C:\x80\xb4\x82)C'
    b'\x01\x83\x05B\x86$I\x03C\x89#F\x05C\xc0\xd2'
    b'\xc1\x89-D\x8a\x18\x82\x0c\x82\x04C\x01\x8b\x15\x84\x08'
    b'\x85\n\x8a\x13\x92\x05\x83\x03\x8a\x11\x93\x03\x88\x01\x8a\x0f'
    b'\x93\x03\x95\r\x94\x02\x97\x0b\x95\x01\x99\t\xb1\x08\xb1\x07'
    b'\xa7\x01\x8b\x06\xa5\x03\x8b\x05\xa4\x04\x8d\x04\xa1\x06\x8e\x03'
    b'\xa0\x07\x90\x02\x9e\x08\x91\x02\x9b\x0b\x91\x02\x99\x0c\x92\x02'
    b'\x98\x0c\x93\x01\x99\x0b\xad\x03\x84\x04\xae\x03\x84\x03\xaf\x03'
    b'\x84\x03\xb0\x02\x84\x02\x82\x01\xaf\x05\x83\x02\x95\x01\x9a\x03'
    b'\x83\x04\x93\x02\xa0\x05\x92\x02\xa1\x04\x92\x02\xa2\x04\x91\x02'
    b'\xa4\x03\x90\x03\xa4\x03\x8e\x04\xa5\x02\x8e\x05\xa6\x01\x8c\x06'
    b'\xa7\x01\x8b\x07\xb1\x08\xb1\t\xaf\x0b\xad\r\xab\x0f\xa9\x11'
    b'\xa7\x13\xa5\x15\xa3\x18\x9f\x1c\x9b \x97%\x91,\x89\x18'
)


_STOPPED = const(0)
_RUNNING = const(1)
_RINGING = const(2)
_REPEAT_MAX = const(99)  # auto stop repeat after 99 runs
_FIELDS = const(1234567890)
_MAX_VIB = const(15)  # max number of second the watch you vibrate

# you can add your own presets here:
_PRESETS = ['2,10', '10,2', '20,5']
_TIME_MODE = const(1)  # if 0: duration of vibration will be discounted
# from timer. if 1: not discounted


class PomodoroApp():
    """Allows the user to set a periodic vibration alarm, Pomodoro style."""
    NAME = 'Pomodoro'
    ICON = icon

    def __init__(self):
        self._already_initialized = False

    def _actual_init(self):
        self.current_alarm = None
        self.nb_vibrat_total = _STOPPED  # number of time it vibrated
        self.last_preset = _STOPPED
        self.last_run = -1  # to keep track of where in the queue we are
        self.state = _STOPPED

        # reloading last value
        try:
            last_val = wasp.system.get("pomodoro")
            self.nb_vibrat_per_alarm = int(last_val[0])
            self.queue = last_val[1]
        except:
            self.queue = _PRESETS[0]
            self.nb_vibrat_per_alarm = 10 # number of times to vibrate each time
        return True

    def foreground(self):
        if not self._already_initialized:
            self._already_initialized = self._actual_init()
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
                if random.random() > 0.7:  # one very long vibration
                    wasp.watch.vibrator.pulse(duty=random.randint(3, 60),
                                              ms=900)
                else:  # burst of vibration
                    max_dur = 900
                    done = 0
                    while done <= max_dur:
                        new_vibr = random.randint(20, 200)
                        new_sleep = random.randint(0, 300)
                        while done + new_vibr + new_sleep > max_dur * 1.1:
                            new_vibr = random.randint(20, 200)
                            new_sleep = random.randint(0, 300)
                        wasp.watch.vibrator.pulse(duty=3, ms=new_vibr)
                        wasp.watch.time.sleep(new_sleep * 0.001)
                        done += new_vibr + new_sleep
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
                self.nb_vibrat_per_alarm = max(1, (self.nb_vibrat_per_alarm + 1) % (_MAX_VIB + 1))
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
        if first_run or _TIME_MODE == 1:
            self.current_alarm = now + max(m * 60, 1)
        else:
            self.current_alarm = now + max(m * 60 - self.nb_vibrat_per_alarm, 1)
        wasp.system.set_alarm(self.current_alarm, self._alert)
        self._draw()
        if hasattr(wasp.system, "set") and callable(wasp.system.set):
            wasp.system.set("pomodoro", [self.nb_vibrat_per_alarm, self.queue])

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
        sbar = wasp.system.bar
        sbar.clock = True
        sbar.draw()

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
