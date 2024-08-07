# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2021 Francesco Gazzetta
"""Level application
~~~~~~~~~~~~~~~~~~~~

This app shows a dot that moves depending on the orientation of the watch.
A tap opens a menu with the option to calibrate or reset the level.
To calibrate, place the watch on a flat surface, then tap the "Calibrate"
button while ensuring the watch is stationary.

.. figure:: res/screenshots/LevelApp.png
    :width: 179
"""

import wasp
import watch
import widgets
from micropython import const

_X_MAX = const(240)
_Y_MAX = const(240)
_X_CENTER = const(120)
_Y_CENTER = const(120)

class LevelApp():
    NAME = "Level"
    # 2-bit RLE, 96x64, generated from res/level_icon.png, 410 bytes
    ICON = (
        b'\x02'
        b'`@'
        b'?\xff\xff\xff\xff\xff\xd0@\xa8L\x80r\x82\xc0\xfd\xf0'
        b'\x82L\x13M\x82@\xb0O\xc1\x05\xc1\x04\xc1\x05\xc1O'
        b'\x82\x80\xa8\x8d\x11\x8e\xc0r\xc2O@\xfdA\x05A\x04'
        b'A\x05A\x80\xb0\x8f\xc2\xc0\xa8\xce\x10\xce@rB\x8f'
        b'\x80\xfd\x81\x05\x81\x04\x81\x05\x81\xc0\xb0\xcfB@\xa8N'
        b'\x10N\x80r\x82\xcf\xc0\xfd\xc1\x05\xc1\x04\xc1\x05\xc1@'
        b'\xb0O\x82\x80\xa8\x8e\x10\x8e\xc0r\xc2O@\xfdA\x05'
        b'A\x04A\x05A\x80\xb0\x8f\xc2\xc0\xa8\xce\x10\xce@r'
        b'B\x8f\x80\xfd\x81\xc0\xb0\xc1\x04\x81\x04\x81\x04\xc1\x81\xcf'
        b'B@\xa8N\x10N\x80r\x82\xcf\xc0\xfd\xc1@\xb0C'
        b'\x02\xc1\x04\xc1\x02C\xc1O\x82\x80\xa8\x8e\x10\x8e\xc0r'
        b'\xc2O@\xfdA\x80\xb0\x85A\x84A\x85A\x8f\xc2\xc0'
        b'\xa8\xce\x10\xce@rB\x8f\x80\xfd\x81\xc0\xb0\xc5\x81\xc4'
        b'\x81\xc5\x81\xcfB@\xa8N\x10N\x80r\x82\xcf\xc0\xfd'
        b'\xc1@\xb0E\xc1D\xc1E\xc1O\x82\x80\xa8\x8e\x10\x8e'
        b'\xc0r\xc2O@\xfdA\x80\xb0\x85A\x84A\x85A\x8f'
        b'\xc2\xc0\xa8\xce\x10\xce@rC\x8e\x80\xfd\x81\xc0\xb0\xc5'
        b'\x81\xc4\x81\xc5\x81\xceC@\xa8N\x10O\x80r\x82\xce'
        b'\xc0\xfd\xc1@\xb0E\xc1D\xc1E\xc1N\x82\x80\xa8\x8f'
        b'\x10\x8f\xc0r\xc3M@\xfdA\x80\xb0\x85A\x84A\x85'
        b'A\x8d\xc3\xc0\xa8\xcf\x10\xd0@rD\x8b\x80\xfd\x81\xc0'
        b'\xb0\xc5\x81\xc4\x81\xc5\x81\xcbD@\xa8P\x10Q\x80r'
        b'\xaeQ\x10S\xaaS\x10\x7f\x11\x10\x7f\x11\x10\x7f\x11\x10'
        b'\x7f\x11\x10\x7f\x11\x10\x7f\x11\x10\x7f\x11\x10\x7f\x11\x10\x7f'
        b'\x11\x10\x7f\x11\x10\x7f\x11\x10\x7f\x11\x11\x7f\x0f\x13\x7f\r'
        b'?\xff\xff\xff\xff\xff\xd0'
    )

    def __init__(self):
        self.old_xy = (0,0)
        self.calibration = (0,0)
        self.prompt = False
        self.calibrate = widgets.Button(20, 20, 200, 60, 'Calibrate')
        self.reset = widgets.Button(20, 90, 200, 60, 'Reset')
        self.cancel = widgets.Button(20, 160, 200, 60, 'Cancel')

    def foreground(self):
        self.prompt = False # in case the watch went to sleep with prompt on
        self._draw()
        wasp.system.request_event(wasp.EventMask.TOUCH)
        wasp.system.request_tick(125)

    def _draw(self):
        wasp.watch.drawable.fill()
        self._update()

    def _update(self):
        if not self.prompt:
            draw = wasp.watch.drawable
            # Clear the old bubble
            draw.fill(None, self.old_xy[0] - 3 + _X_CENTER, self.old_xy[1] - 3 + _Y_CENTER, 6, 6)
            # draw guide lines
            draw.line(0, _Y_CENTER, _X_MAX, _Y_CENTER, color = wasp.system.theme('mid'))
            draw.line(_X_CENTER, 0, _X_CENTER, _Y_MAX, color = wasp.system.theme('mid'))
            (new_x, new_y, _) = watch.accel.accel_xyz()
            # We clamp and scale the values down a bit to make them fit better,
            # and apply the calibration.
            # The scaling factor is negative because when gravity pulls in one
            # direction we want the bubble to go the other direction.
            new_x = min(_X_CENTER, max(-_X_CENTER, (new_x-self.calibration[0])//-3))
            new_y = min(_Y_CENTER, max(-_Y_CENTER, (new_y-self.calibration[1])//-3))
            # Draw the new bubble
            draw.fill(wasp.system.theme('bright'), new_x - 3 + _X_CENTER, new_y - 3 + _Y_CENTER, 6, 6)
            self.old_xy = (new_x, new_y)

    def tick(self, ticks):
        self._update()
        wasp.system.keep_awake()

    def touch(self, event):
        if self.prompt:
            # Handle buttons
            if self.calibrate.touch(event):
                (x, y, _) = watch.accel.accel_xyz()
                self.calibration = (x, y)
            if self.reset.touch(event):
                self.calibration = (0,0)
            #if self.cancel.touch(event):
            #    pass

            # reset the color (buttons set it to blue) and disable prompt
            wasp.watch.drawable.set_color(wasp.system.theme('bright'))
            self.prompt = False
            self._draw()
        else:
            # Draw menu
            self.prompt = True
            wasp.watch.drawable.fill()
            self.calibrate.draw()
            self.reset.draw()
            self.cancel.draw()
