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

# 2-bit RLE, generated from res/alarm_icon.png, 390 bytes
icon = (
    b'\x02'
    b'`@'
    b'\x17@\xd2G#G-K\x1fK)O\x1bO&O'
    b'\n\x80\xb4\x89\x0bN$N\x08\x91\tM"M\x07\x97'
    b'\x07M!L\x06\x9b\x07K K\x06\x9f\x06K\x1fJ'
    b'\x05\xa3\x05J\x1eJ\x05\x91\xc0\xd0\xc3\x91\x05J\x1dI'
    b'\x05\x8c\xcf\x8c\x05I\x1dH\x05\x8b\xd3\x8b\x05H\x1dG'
    b'\x05\x8a\xd7\x8a\x05G\x1dG\x04\x89\xdb\x89\x05F\x1dF'
    b'\x04\x89\xcc\x05\xcc\x89\x04F\x1dE\x04\x89\xcd\x05\xcd\x89'
    b'\x04E\x1eD\x03\x88\xce\x07\xce\x88\x04C\x1fC\x04\x88'
    b'\xce\x07\xce\x88\x04C\x1fC\x03\x88\xcf\x07\xcf\x88\x04A'
    b'!A\x04\x87\xd0\x07\xd0\x87\x04A%\x87\xd1\x07\xd1\x87'
    b")\x87\xd1\x07\xd1\x87(\x87\xd2\x07\xd2\x87'\x87\xd2\x07"
    b"\xd2\x87'\x86\xd3\x07\xd3\x86&\x87\xd3\x07\xd3\x87%\x86"
    b'\xd4\x07\xd4\x86%\x86\xd4\x07\xd4\x86%\x86\xd4\x07\xd4\x86'
    b'$\x87\xd4\x07\xd4\x87#\x87\xd4\x07\xd4\x87#\x87\xd4\x07'
    b'\xd4\x87#\x86\xd4\x08\xd5\x86#\x86\xd3\t\xd5\x86#\x86'
    b'\xd2\t\xd6\x86#\x87\xd0\n\xd5\x87#\x87\xcf\n\xd6\x87'
    b'#\x87\xce\n\xd7\x87$\x86\xce\t\xd8\x86%\x86\xce\x08'
    b'\xd9\x86%\x86\xcd\x08\xda\x86%\x87\xcc\x07\xda\x87%\x87'
    b"\xcc\x06\xdb\x86'\x87\xcc\x03\xdc\x87'\x87\xeb\x87(\x87"
    b'\xe9\x87)\x87\xe9\x87*\x87\xe7\x87+\x88\xe5\x88,\x87'
    b'\xe5\x87-\x88\xe3\x88.\x88\xe1\x880\x89\xdd\x892\x89'
    b'\xdb\x893\x8b\xd7\x8b2\x8d\xd4\x8e0\x91\xcf\x91.\x97'
    b'\xc5\x97,\xb5+\x88\x03\x9f\x03\x88*\x88\x05\x9d\x05\x88'
    b')\x87\t\x97\t\x87*\x85\x0c\x93\x0c\x85,\x83\x11\x8b'
    b'\x11\x83\x17'
)

class AlarmApp():
    """Allows the user to set a vibration alarm.
    """
    NAME = 'Alarm'
    ICON = icon

    def __init__(self):
        """Initialize the application."""
        self.active = widgets.Checkbox(104, 200)
        self.hours = widgets.Spinner(50, 60, 0, 23, 2)
        self.minutes = widgets.Spinner(130, 60, 0, 59, 2)

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
