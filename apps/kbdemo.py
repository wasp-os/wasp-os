# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2023 Samuel Sloniker
"""Keyboard demonstration app
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This app demonstrates the functionality of the Wasp-os keyboard.


.. figure:: res/screenshots/KbdemoApp.png
    :width: 179
"""

import wasp
import fonts


class KbdemoApp:
    NAME = "KBDemo"

    def __init__(self):
        self.kb = wasp.Keyboard(self.set_message)
        self.msg = "Tap anywhere on the screen to change this message"

    def set_message(self, message):
        if message.strip():
            self.msg = message
        self._draw()

    def foreground(self):
        wasp.system.request_event(wasp.EventMask.TOUCH)
        if not self.kb.draw():
            self._draw()

    def touch(self, event):
        if not self.kb.touch(event):
            self.kb.open()

    def _draw(self):
        draw = wasp.watch.drawable
        draw.fill()
        draw.set_font(fonts.sans24)

        last = 0
        y = 0
        for i in draw.wrap(self.msg, 240)[1:]:
            draw.string(self.msg[last:i], 0, y)
            last = i
            y += 24
