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

# 1-bit RLE, generated from res/alarm_icon.png, 277 bytes
icon = (
    96, 64,
    b'\xff\x00\xff\x00\xbf\x05\x1f\x055\x08\x0b\x07\x0b\t1\n'
    b'\x06\x0f\x07\t0\n\x06\x11\x06\n.\n\x04\x17\x04\n'
    b'-\t\x04\x19\x04\t,\t\x03\x1e\x02\t+\x08\x03 '
    b'\x02\x08+\x07\x03\r\x07\x0e\x02\x07+\x06\x03\r\t\r'
    b'\x03\x06+\x05\x03\x0b\x0f\x0b\x03\x05+\x04\x03\n\x13\n'
    b'\x03\x04,\x02\x04\t\x15\t\x04\x022\t\x17\t6\t'
    b'\x19\t4\n\x1a\t3\t\r\x01\x0e\x083\x07\x0e\x03'
    b'\x0e\x072\x08\x0e\x03\x0e\x081\x07\x0f\x03\x0f\x071\x07'
    b'\x0f\x03\x0f\x071\x07\x0f\x03\x0f\x071\x06\x10\x03\x10\x06'
    b'0\x07\x10\x03\x10\x07/\x07\x10\x03\x10\x07/\x07\x10\x03'
    b'\x10\x07/\x07\x0f\x04\x10\x07/\x07\x0e\x04\x11\x07/\x07'
    b'\r\x04\x12\x070\x06\x0c\x04\x13\x061\x07\n\x04\x13\x07'
    b'1\x07\n\x03\x14\x071\x07\n\x02\x15\x071\x08\x1f\x08'
    b'2\x07\x1f\x073\x08\x1d\x083\t\x1b\t4\t\x19\t'
    b'6\t\x17\t8\t\x15\t9\n\x13\n:\x0b\x0f\x0b'
    b'<\x0e\x08\r>!@\x1fB\x1dC\x1e@!?\x05'
    b'\x03\x11\x03\x05?\x04\t\x07\t\x04@\x02\x0b\x05\x0b\x02'
    b'\xff\x00\xff\x00a'
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
        if self.ringing:
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
        wasp.watch.vibrator.pulse(duty=50, ms=500)
        wasp.system.keep_awake()

    def touch(self, event):
        """Notify the application of a touchscreen touch event."""
        draw = wasp.watch.drawable
        if event[1] in range(90, 150) and event[2] in range(180,240):
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
