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
import fonts
import time
import widgets

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
        self.active = widgets.Checkbox(104, 200)
        self.hours = widgets.Spinner(50, 60, 0, 24, 2)
        self.minutes = widgets.Spinner(130, 60, 0, 60, 2)

        self.hours.value = 7
        self.ringing = False

    def foreground(self):
        """Activate the application."""
        self._draw()
        wasp.system.request_event(wasp.EventMask.TOUCH)
        wasp.system.request_tick(1000)
        if self.active.state:
            wasp.system.cancel_alarm(self.current_alarm, self._alert)

    def background(self):
        """De-activate the application."""
        if self.active.state:
            self._set_current_alarm()
            wasp.system.set_alarm(self.current_alarm, self._alert)
            if self.ringing:
                self.ringing = False

    def tick(self, ticks):
        """Notify the application that its periodic tick is due."""
        if self.ringing:
            wasp.watch.vibrator.pulse(duty=50, ms=500)
            wasp.system.keep_awake()
        else:
            wasp.system.bar.update()

    def touch(self, event):
        """Notify the application of a touchscreen touch event."""
        if self.ringing:
            mute = wasp.watch.display.mute
            self.ringing = False
            mute(True)
            self._draw()
            mute(False)
        elif self.hours.touch(event) or self.minutes.touch(event) or \
             self.active.touch(event):
            pass

    def _draw(self):
        """Draw the display from scratch."""
        draw = wasp.watch.drawable
        if not self.ringing:
            draw.fill()

            sbar = wasp.system.bar
            sbar.clock = True
            sbar.draw()

            draw.set_font(fonts.sans28)
            draw.string(':', 110, 120-14, width=20)

            self.active.draw()
            self.hours.draw()
            self.minutes.draw()
        else:
            draw.fill()
            draw.set_font(fonts.sans24)
            draw.string("Alarm", 0, 150, width=240)
            draw.blit(icon, 73, 50)

    def _alert(self):
        self.ringing = True
        wasp.system.wake()
        wasp.system.switch(self)

    def _set_current_alarm(self):
        now = wasp.watch.rtc.get_localtime()
        yyyy = now[0]
        mm = now[1]
        dd = now[2]
        HH = self.hours.value
        MM = self.minutes.value
        if HH < now[3] or (HH == now[3] and MM <= now[4]):
            dd += 1
        self.current_alarm = (time.mktime((yyyy, mm, dd, HH, MM, 0, 0, 0, 0)))
