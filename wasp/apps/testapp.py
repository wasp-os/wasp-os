# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 Daniel Thompson

import machine
import wasp

class TestApp():
    """Simple test application.
    """

    def __init__(self):
        self.tests = ('Touch', 'String')
        self.test = self.tests[0]

    def foreground(self):
        """Activate the application."""
        self.on_screen = ( -1, -1, -1, -1, -1, -1 )
        self.draw()
        wasp.system.request_event(wasp.EventMask.TOUCH |
                                  wasp.EventMask.SWIPE_UPDOWN)

    def background(self):
        """De-activate the application (without losing state)."""
        pass

    def sleep(self):
        return False

    def swipe(self, event):
        tests = self.tests
        i = tests.index(self.test) + 1
        if i >= len(tests):
            i = 0
        self.test = tests[i]
        self.draw()

    def touch(self, event):
        draw = wasp.watch.drawable
        if self.test == 'Touch':
            draw.string('({}, {})'.format(event[1], event[2]),
                    0, 108, width=240)
        elif self.test == 'String':
            draw.fill(0, 0, 30, 240, 240-30)
            t = machine.Timer(id=1, period=8000000)
            t.start()
            draw.string("The quick brown", 12, 24+24)
            draw.string("fox jumped over", 12, 24+48)
            draw.string("the lazy dog.", 12, 24+72)
            draw.string("0123456789", 12, 24+120)
            draw.string('!"£$%^&*()', 12, 24+144)
            elapsed = t.time()
            t.stop()
            del t
            draw.string('{}s'.format(elapsed / 1000000), 12, 24+192)

        return True

    def draw(self):
        """Redraw the display from scratch."""
        wasp.watch.display.mute(True)
        wasp.watch.drawable.fill()
        wasp.watch.drawable.string('{} test'.format(self.test),
                0, 6, width=240)
        wasp.watch.display.mute(False)
