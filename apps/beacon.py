# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2021 Francesco Gazzetta
"""Beacon application
~~~~~~~~~~~~~~~~~~~~~

Flash the relatively powerful HRS LED repeatedly, mostly for signaling purposes.

Frequency and intensity can be changed.

The blinking is handled by the HRS, so this app consumes very little power.
With BLE and/or step counter disabled and blinking frequency set to the minimum,
the watch's battery will last for many days.

.. figure:: res/screenshots/BeaconApp.png
    :width: 179
"""

import wasp
import machine
from micropython import const

class BeaconApp():
    NAME = "Beacon"
    # 2-bit RLE, 96x64, generated from res/beacon_icon.png, 336 bytes
    ICON = (
        b'\x02'
        b'`@'
        b'?\xff\x11@\xfcB?\x1dB\x80z\x82B?\x1aA'
        b'\x86A?\x18A\x88A?\t\xc0\x18\xc3\nA\x8aA'
        b'\n\xc3=\xc5\x04N\x04\xc5?\x06\xc3\x02A\xcaA\x02'
        b'\xc3?\x10A\xcaA?\x08\xcb\x02A\xc3@\x1eD\xc3'
        b'\x80\xfc\x81\x02\xcc9\xcb\x01\x81\xc4D\xc4\x81\x01\xcc?'
        b'\x06\x81\xcc\x81?\x0f\xc3\x01\x81\xcc\x81\x01\xc3?\x06\xc5'
        b'\x04\x8e\x04\xc5=\xc3\t\x81\xc0z\xcc\x81\t@\x18C'
        b'?\x07\x81\xcc\x81?\x12\x81\xce\x81?\x11\x81\xce\x81?'
        b'\x11\x81\xce\x81?\x11\x81\xce\x81?\x11\x81\xce\x81?\x11'
        b'\x81\xce\x81?\x11\x81\xce\x81?\x10\x81\xd0\x81?\x0f\x81'
        b'\xd0\x81?\x0f\x92?\x0f\x81\x80\x81\x90\xc0\xfc\xc1?\x0f'
        b'\xc1\x90\xc1?\x0f\xc1\x90\xc1?\x0e\xc1\x92\xc1?\r\xc1'
        b'\x92\xc1?\r\xc1\x92\xc1?\r\xc1\x92\xc1?\r\xc1\x92'
        b'\xc1?\r\xc1\x92\xc1?\r\xc1\x92\xc1?\x0c\xc1\x94\xc1'
        b'?\x0b\xd6?\x0b\xc1@zT\xc1?\x0b\xc1T\xc1?'
        b'\x0b\xc1T\xc1?\x0b\xc1T\xc1?\n\xc1V\xc1?\t'
        b'\xc1V\xc1?\t\xc1V\xc1?\t\xc1V\xc1?\t\xc1'
        b'V\xc1?\t\xc1V\xc1?\t\xc1V\xc1?\x08\xda?'
        b'\x07\xc1\x98\xc1?\x07\xc1\x98\xc1?\x07\xc1\x98\xc1?\x07'
        b'\xc1\x98\xc1?\x07\xc1\x98\xc1?\x06\xc1\x9a\xc1?\x05\xc1'
        b'\x9a\xc1?\x05\xc1\x9a\xc1?\x05\xdc?\xff\x04'
    )


    def __init__(self):
        self._checkbox = wasp.widgets.Checkbox(10, 45, "Enable beacon")
        self._slider_current = wasp.widgets.Slider(4, 10, 110, 0x27e4)
        self._slider_wait_time = wasp.widgets.Slider(8, 10, 180)

    def foreground(self):
        wasp.system.bar.clock = True
        self._draw()
        wasp.system.request_event(wasp.EventMask.TOUCH)

    def _draw(self):
        draw = wasp.watch.drawable
        draw.fill()
        wasp.system.bar.draw()
        self._checkbox.draw()
        draw.string("Intensity:", 10, 85)
        self._slider_current.draw()
        draw.string("Frequency:", 10, 155)
        self._slider_wait_time.draw()
        self._draw_preview()

    def touch(self, event):
        if self._checkbox.touch(event):
            if self._checkbox.state:
                wasp.watch.hrs.enable()
                wasp.watch.hrs.set_hwt(self._slider_wait_time.value)
                wasp.watch.hrs.set_drive(self._slider_current.value)
            else:
                wasp.watch.hrs.disable()
            self._checkbox.update()
        elif event[2] >= 180:
            if self._slider_wait_time.touch(event):
                wasp.watch.hrs.set_hwt(self._slider_wait_time.value)
                self._slider_wait_time.update()
                self._draw_preview()
        elif event[2] >= 110:
            if self._slider_current.touch(event):
                wasp.watch.hrs.set_drive(self._slider_current.value)
                self._slider_current.update()
                self._draw_preview()
        wasp.system.bar.update()

    def _draw_preview(self):
        """
        Draw a dashed line representing intensity and frequency
        with thickness and separation of dashes
        """
        draw = wasp.watch.drawable
        draw.fill(None, 10, 220, 227, 20)
        x = 10
        while x < 220:
            wasp.watch.drawable.fill(0x27e4, x, 227, 8, (self._slider_current.value + 1) * 3)
            x += (8 - self._slider_wait_time.value) * 8
