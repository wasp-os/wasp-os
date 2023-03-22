# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2021 Francesco Gazzetta

"""DisaBLE
~~~~~~~~~~

Disable BLE to save energy and enhance privacy.

This app shows the bluetooth status and provides a button to disable/enable it.
Unfortunately, re-enabling bluetooth normally has some issues, so as a
workaround the "enable" button restarts the watch.

.. figure:: res/screenshots/DisaBLEApp.png
    :width: 179
"""

import wasp
import widgets
import ble

class DisaBLEApp():
    NAME = 'DisaBLE'
    # 1-bit RLE, 96x64, generated from res/disaBLE_icon.png, 167 bytes
    ICON = (
        96, 64,
        b'\xff\x00\xff\x00\xff\x00\xff\x00g\x02]\x03\\\x03\\\x03'
        b'\\\x03J\x01\x11\x03K\x02\x0f\x03L\x03\r\x03M\x04'
        b'\x0b\x03N\x05\t\x03O\x06\x07\x03P\x07\x05\x03Q\x03'
        b'\x01\x04\x03\x03L\x02\x04\x03\x02\x04\x01\x03L\x04\x03\x03'
        b'\x03\x06N\x04\x02\x03\x02\x06P\x04\x01\x03\x01\x06R\r'
        b'T\x0bV\tX\x07Y\x06Y\x07X\tV\x0bT\x08'
        b'\x01\x04R\t\x02\x04P\x06\x01\x03\x03\x04P\x04\x02\x03'
        b'\x02\x04Q\x03\x03\x03\x01\x04Q\x03\x04\x07Q\x03\x05\x06'
        b'Q\x03\x06\x05Q\x03\x07\x04Q\x03\x08\x03Q\x03\t\x02'
        b'Q\x03\n\x01Q\x03\\\x03\\\x03\\\x03]\x02\xff\x00'
        b'\xff\x00\xff\x00\xff\x00g'
    )

    def foreground(self):
        self._draw()
        wasp.system.request_event(wasp.EventMask.TOUCH)

    def _draw(self):
        draw = wasp.watch.drawable
        draw.set_color(wasp.system.theme('bright'))
        draw.fill()
        draw.string('BLE status: ' + ('ON' if ble.enabled() else 'OFF'), 0, 60, width=240)
        self._btn = widgets.Button(10, 120, 220, 80, 'Disable' if ble.enabled() else 'Reboot to enable')
        self._btn.draw()

    def touch(self, event):
        if self._btn.touch(event):
            if ble.enabled():
                ble.disable()
                self._draw()
            else:
                wasp.machine.reset()
        else:
            self._draw()
