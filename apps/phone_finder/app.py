# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2023 Adam Blair
"""Phone finder application
~~~~~~~~~~~~~~~~~~~~~~~~~~~

An application to find a phone connected via Gadgetbridge.

    .. figure:: res/screenshots/PhoneFinderApp.png
        :width: 179

        Screenshot of the Phone Finder Application

"""

import wasp
import fonts
import widgets
from gadgetbridge import send_cmd

# 2-bit RLE, 96x64, generated from res/phone_finder_icon.png, 403 bytes
icon = (
    b'\x02'
    b'`@'
    b'?\xff\xff\x87@\xd0G?\x17C\x07C?\x12B\r'
    b'B?\x0fA\x11A?\rA\x13A?\x0bA\x15A'
    b'?\tA?\x1fA!\x80\xb4\x84:A\rG\r\x84'
    b'9A\x0cB\x07B?\tA\x0bA\x0bA?\x08A'
    b'\nA\rA\t\x848A\nA\x18\x848A\tA'
    b'\tD\x0c\x848A\x08A\x08B\x04B\n\x848A'
    b'\x08A\x06B\x08A\t\x848A\x07A\x06A\x14A'
    b'\x838A\x07A\x06A\x01A\x91B\x83A7A\x07'
    b'A\x05A\x01A\x98A7A\x06A\x05A\x01\x82\x16'
    b'\x827A\x06A\x04A\x02\x82\x04N\x04\x827A\x06'
    b'A\x04A\x02\x82\x04N\x04\x828A\x05A\x04A\x02'
    b'\x82\x04N\x04\x828A\x06A\x03A\x02\x82\x16\x829'
    b'A\x05A\x04A\x01\x82\x02R\x02\x82:A\x05A\x03'
    b'A\x01\x82\x02R\x02\x82;A\x05A\x03A\x82\x02R'
    b'\x02\x82<A\x05A\x02A\x82\x02R\x02\x82?\x07\x82'
    b'\x02R\x02\x82?\x07\x82\x02R\x02\x82?\x07\x82\x02R'
    b'\x02\x82?\x07\x82\x02R\x02\x82?\x07\x82\x02R\x02\x82'
    b'?\x07\x82\x02R\x02\x82?\x07\x82\x02R\x02\x82?\x07'
    b'\x82\x02R\x02\x82?\x07\x82\x02R\x02\x82?\x07\x82\x02'
    b'R\x02\x82?\x07\x82\x02R\x02\x82?\x07\x82\x02R\x02'
    b'\x82?\x07\x82\x02R\x02\x82?\x07\x82\x02R\x02\x82?'
    b'\x07\x82\x02R\x02\x82?\x07\x82\x02R\x02\x82?\x07\x82'
    b'\x02R\x02\x82?\x07\x82\x02R\x02\x82?\x07\x82\x02R'
    b'\x02\x82?\x07\x82\x16\x82?\x07\x82\x06J\x06\x82?\x07'
    b'\x82\x16\x82?\x07A\x98A?\x08A\x96A?\xff\xc1'
)

class PhoneFinderApp():
    """Allows the user to set a vibration alarm.
    """
    NAME = 'Finder'
    ICON = icon

    def __init__(self):
        """Initialize the application."""
        pass

    def foreground(self):
        """Activate the application."""
        self.ring_btn = widgets.ToggleButton(20, 120, 200, 60, 'Ring')

        self._draw()
        wasp.system.request_event(wasp.EventMask.TOUCH)
        wasp.system.request_tick(1000)

    def background(self):
        """De-activate the application."""
        self.ring_btn = None
        del self.ring_btn

    def tick(self, ticks):
        """Notify the application that its periodic tick is due."""
        wasp.system.bar.update()

    def touch(self, event):
        """Notify the application of a touchscreen touch event."""
        if self.ring_btn.touch(event):
            if self.ring_btn.state:
                send_cmd('{"t":"findPhone", "n":"true"} ')
            else:
                send_cmd('{"t":"findPhone", "n":"false"} ')

    def _draw(self):
        """Draw the display from scratch."""
        draw = wasp.watch.drawable
        draw.fill()
        sbar = wasp.system.bar
        sbar.clock = True
        sbar.draw()

        draw.set_font(fonts.sans24)
        draw.string('Find phone', 60, 70, width=120)
        self.ring_btn.draw()