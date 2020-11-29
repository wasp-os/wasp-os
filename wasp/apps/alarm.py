# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 Daniel Thompson
# Copyright (C) 2020 Joris Warmbier
"""Alarm Application
~~~~~~~~~~~~~~~~~~~~

An application to set a vibration alarm. All settings can be accessed from the Watch UI.

    .. figure:: res/AlarmApp.png
        :width: 179

        Screenshot of the Alarm Application

"""

import wasp
import time

# 2-bit RLE, generated from res/alarm_icon.png, 285 bytes
icon = (
    b'\x02'
    b'`@'
    b'?\xff\xff\x80\xc5\x1f\xc55\xc8\x0b\xc7\x0b\xc91\xca\x06'
    b'\xcf\x07\xc90\xca\x06\xd1\x06\xca.\xca\x04\xd7\x04\xca-'
    b'\xc9\x04\xd9\x04\xc9,\xc9\x03\xde\x02\xc9+\xc8\x03\xe0\x02'
    b'\xc8+\xc7\x03\xcd\x07\xce\x02\xc7+\xc6\x03\xcd\t\xcd\x03'
    b'\xc6+\xc5\x03\xcb\x0f\xcb\x03\xc5+\xc4\x03\xca\x13\xca\x03'
    b'\xc4,\xc2\x04\xc9\x15\xc9\x04\xc22\xc9\x17\xc96\xc9\x19'
    b'\xc94\xca\x1a\xc93\xc9\r\xc1\x0e\xc83\xc7\x0e\xc3\x0e'
    b'\xc72\xc8\x0e\xc3\x0e\xc81\xc7\x0f\xc3\x0f\xc71\xc7\x0f'
    b'\xc3\x0f\xc71\xc7\x0f\xc3\x0f\xc71\xc6\x10\xc3\x10\xc60'
    b'\xc7\x10\xc3\x10\xc7/\xc7\x10\xc3\x10\xc7/\xc7\x10\xc3\x10'
    b'\xc7/\xc7\x0f\xc4\x10\xc7/\xc7\x0e\xc4\x11\xc7/\xc7\r'
    b'\xc4\x12\xc70\xc6\x0c\xc4\x13\xc61\xc7\n\xc4\x13\xc71'
    b'\xc7\n\xc3\x14\xc71\xc7\n\xc2\x15\xc71\xc8\x1f\xc82'
    b'\xc7\x1f\xc73\xc8\x1d\xc83\xc9\x1b\xc94\xc9\x19\xc96'
    b'\xc9\x17\xc98\xc9\x15\xc99\xca\x13\xca:\xcb\x0f\xcb<'
    b'\xce\x08\xcd>\xe1?\x01\xdf?\x03\xdd?\x04\xde?\x01'
    b'\xe1?\x00\xc5\x03\xd1\x03\xc5?\x00\xc4\t\xc7\t\xc4?'
    b'\x01\xc2\x0b\xc5\x0b\xc2?\xff\xff"'
)

class AlarmApp():
    """Allows the user to set a vibration alarm.
    """
    NAME = 'Alarm'
    ICON = icon

    def __init__(self):
        """Initialize the application."""

        self.active = False
        self.ringing = False
        self.hours = 0
        self.minutes = 0

        self._set_current_alarm()

    def foreground(self):
        """Activate the application."""
        self._draw()
        wasp.system.request_event(wasp.EventMask.TOUCH)
        wasp.system.request_tick(1000)
        wasp.system.cancel_alarm(self.current_alarm, self._alert)

    def background(self):
        """De-activate the application."""
        if self.active:
            self._set_current_alarm()
            wasp.system.set_alarm(self.current_alarm, self._alert)
            if self.ringing:
                self.ringing = False

    def tick(self, ticks):
        """Notify the application that its periodic tick is due."""
        if self.ringing:
            wasp.watch.vibrator.pulse(duty=50, ms=500)
            wasp.system.keep_awake()

    def touch(self, event):
        """Notify the application of a touchscreen touch event."""
        draw = wasp.watch.drawable
        if self.ringing:
            mute = wasp.watch.display.mute
            self.ringing = False
            mute(True)
            self._draw()
            mute(False)

        elif event[1] in range(90, 150) and event[2] in range(180,240):
            self.active = not self.active

        elif event[1] in range(30,90):
            if event[2] in range(40,100):
                self.hours += 1
                if self.hours > 23:
                    self.hours = 0

            elif event[2] in range(120,180):
                self.hours -= 1
                if self.hours < 0:
                    self.hours = 23

        elif event[1] in range(150,210):
            if event[2] in range(40,100):
                self.minutes += 1
                if self.minutes > 59:
                    self.minutes = 0

            elif event[2] in range(120,180):
                self.minutes -= 1
                if self.minutes < 0:
                    self.minutes = 59

        self._update()

    def _draw(self):
        """Draw the display from scratch."""
        draw = wasp.watch.drawable
        if not self.ringing:
            draw.fill()
            draw.string(self.NAME, 0, 6, width=240)

            draw.fill(0xffff, 120, 112, 2, 2)
            draw.fill(0xffff, 120, 106, 2, 2)

            for posx in [40,160]:
                draw.string("+", posx, 60, width=40)
                draw.string("-", posx, 140, width=40)

            draw.fill(0xffff, 100, 190, 40, 40)

            self._update()
        else:
            draw.fill()
            draw.string("Alarm", 0, 150, width=240)
            draw.blit(icon, 73, 50)

    def _update(self):
        """Update the dynamic parts of the application display."""
        draw = wasp.watch.drawable
        if self.active:
            draw.fill(0x001f, 102, 192, 36, 36)
        else:
            draw.fill(0x0000, 102, 192, 36, 36)

        if self.hours < 10:
            draw.string("0"+str(self.hours), 10, 100, width=100)
        else:
            draw.string(str(self.hours), 10, 100, width=100)

        if self.minutes < 10:
            draw.string("0"+str(self.minutes), 130, 100, width=100)
        else:
            draw.string(str(self.minutes), 130, 100, width=100)

    def _alert(self):
        self.ringing = True
        wasp.system.wake()
        wasp.system.switch(self)

    def _set_current_alarm(self):
        now = wasp.watch.rtc.get_localtime()
        yyyy = now[0]
        mm = now[1]
        dd = now[2]
        if self.hours < now[3] or (self.hours == now[3] and self.minutes <= now[4]):
            dd += 1
        self.current_alarm = (time.mktime((yyyy, mm, dd, self.hours, self.minutes, 0, 0, 0, 0)))
