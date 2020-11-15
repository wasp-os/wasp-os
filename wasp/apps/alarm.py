# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 Daniel Thompson
"""The complete set of wasp-os application entry points are documented
below as part of a template application. Note that the template does
not rely on any specific parent class. This is because applications in
wasp-os can rely on *duck typing* making a class hierarchy pointless.
"""

import wasp
import icons
import time

class AlarmApp():
    """Template application.

    The template application includes every application entry point. It
    is used as a reference guide and can also be used as a template for
    creating new applications.

    .. data:: NAME = 'Template'

       Applications must provide a short ``NAME`` that is used by the
       launcher to describe the application. Names that are longer than
       8 characters are likely to be abridged by the launcher in order
       to fit on the screen.

    .. data:: ICON = RLE2DATA

       Applications can optionally provide an icon for display by the
       launcher. Applications that expect to be installed on the quick
       ring will not be listed by the launcher and need not provide any
       icon. When no icon is provided the system will use a default
       icon.

       The icon is an opportunity to differentiate your application from others
       so supplying an icon is strongly recommended. The icon, when provided,
       must not be larger than 96x64.

    """
    NAME = 'Alarm'
    ICON = icons.app
    active = False
    hours = 0
    minutes = 0
    ringing = False

    def __init__(self):
        """Initialize the application."""

        self._set_current_alarm()

    def foreground(self):
        """Activate the application."""
        self._draw()
        wasp.system.request_event(wasp.EventMask.TOUCH)
        wasp.system.request_tick(1000)

    def background(self):
        """De-activate the application."""
        wasp.system.cancel_alarm(time.mktime(self.current_alarm), self._alert)
        if self.active:
            self._set_current_alarm()
            wasp.system.set_alarm(time.mktime(self.current_alarm), self._alert)
            if self.ringing:
                self.ringing = False
    def tick(self, ticks):
        """Notify the application that its periodic tick is due."""
        if self.ringing:
            wasp.watch.vibrator.pulse(duty=25, ms=500)
            wasp.system.keep_awake()

    def touch(self, event):
        """Notify the application of a touchscreen touch event."""
        draw = wasp.watch.drawable
        if event[1] in range(100, 140) and event[2] in range(190,230):
            self.active = not self.active

        elif event[1] in range(40,80):
            if event[2] in range(50,90):
                self.hours += 1
                if self.hours > 23:
                    self.hours = 0

            elif event[2] in range(130,170):
                self.hours -= 1
                if self.hours < 0:
                    self.hours = 23

        elif event[1] in range(160,200):
            if event[2] in range(50,90):
                self.minutes += 1
                if self.minutes > 59:
                    self.minutes = 0

            elif event[2] in range(130,170):
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
            draw.string("Alarm", 0, 100, width=240)
            

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
        self.current_alarm = (yyyy, mm, dd, self.hours, self.minutes, 0, 0, 0, 0)
