# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 Daniel Thompson

import wasp

import fonts
import icons
import time
import watch

# 2-bit RLE, generated from res/feet.png, 240 bytes
feet = (
    b'\x02'
    b'00'
    b'\x13\xc1-\xc4+\xc6*\xc6*\xc6&\xc3\x01\xc6\t\xc2'
    b'\x1b\xc3\x02\xc5\x08\xc4\x1a\xc4\x01\xc5\x08\xc5\x19\xc4\x02\xc3'
    b'\x08\xc6\x17\xc1\x02\xc3\x02\xc3\x08\xc6\x16\xc3\x02\xc1\x0e\xc6'
    b'\x01\xc3\x12\xc3\x11\xc6\x01\xc3\x13\xc2\x05\xc2\n\xc5\x02\xc3'
    b'\x10\xc2\x01\xc2\x02\xc6\n\xc4\x01\xc4\x10\xc2\x04\xc7\x0b\xc1'
    b'\x03\xc3\x11\xc3\x02\xc8\x10\xc2\x01\xc3\r\xc2\x02\xc9\x13\xc3'
    b'\x0b\xc1\x05\xc9\x0c\xc2\x05\xc3\x0b\xc2\x03\xc9\x0c\xc5\x03\xc2'
    b'\x0c\xc2\x02\xca\x0c\xc6\x05\xc2\t\xc2\x02\xca\x0c\xc7\x03\xc3'
    b'\r\xca\x0c\xc8\x02\xc3\x0c\xca\r\xc9\x02\xc1\r\xca\r\xc9'
    b'\x04\xc2\n\xca\x0e\xc9\x02\xc3\n\xca\x0e\xc9\x02\xc2\x0b\xca'
    b'\x0e\xca\x0e\xca\x0e\xca\x0f\xc9\x0e\xca\x0f\xca\r\xca\x0f\xca'
    b'\r\xca\x10\xcb\x0b\xca\x10\xcc\n\xca\x10\xcd\t\xca\x11\xcc'
    b'\x08\xca\x12\xcc\x07\xcb\x13\xcb\x06\xcb\x14\xcb\x05\xcc\x15\xca'
    b'\x04\xcc\x16\xc9\x05\xcc\x17\xc7\x05\xcd\x17\xc7\x05\xcc\x1a\xc4'
    b"\x07\xcb%\xca&\xca'\xc8)\xc6+\xc4\x0e"
)

class StepCounterApp():
    """Step counter application.

    .. figure:: res/StepsApp.png
        :width: 179

        Screenshot of the step counter application
    """
    NAME = 'Steps'
    ICON = icons.app

    def __init__(self):
        watch.accel.reset()
        self._meter = wasp.widgets.BatteryMeter()
        self._count = 0
        self._last_clock = ( -1, -1, -1, -1, -1, -1 )

    def foreground(self):
        """Activate the application."""
        # Force a redraw (without forgetting the current date)
        lc = self._last_clock
        self._last_clock = (lc[0], lc[1], lc[2], -1, -1, -1)

        self._draw()
        wasp.system.request_tick(1000)

    def tick(self, ticks):
        self._count += 686;
        self._update()

    def _draw(self):
        """Draw the display from scratch."""
        draw = wasp.watch.drawable
        draw.fill()
        draw.blit(feet, 12, 132-24)

        self._last_count = -1
        self._update()
        self._meter.draw()

    def _update(self):
        draw = wasp.watch.drawable

        # Lazy update of the clock and battery meter
        now = wasp.watch.rtc.get_localtime()
        if now[4] != self._last_clock[4]:
            t1 = '{:02}:{:02}'.format(now[3], now[4])
            draw.set_font(fonts.sans28)
            draw.set_color(0x7bef)
            draw.string(t1, 48, 12, 240-96)

            if now[2] != self._last_clock[2]:
                watch.accel.steps = 0
                draw.fill(0, 60, 132-18, 180, 36)

            self._last_clock = now
            self._meter.update()

        count = watch.accel.steps
        t = str(count)
        w = fonts.width(fonts.sans36, t)
        draw.set_font(fonts.sans36)
        draw.set_color(0xfff0)
        draw.string(t, 228-w, 132-18)
