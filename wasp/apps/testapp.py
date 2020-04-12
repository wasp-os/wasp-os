# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 Daniel Thompson

import machine
import wasp
import icons

class TestApp():
    """Simple test application.
    """
    NAME = 'Self Test'
    ICON = icons.app

    def __init__(self):
        self.tests = ('Button', 'Crash', 'RLE', 'String', 'Touch', 'Wrap')
        self.test = self.tests[0]
        self.scroll = wasp.widgets.ScrollIndicator()

    def foreground(self):
        """Activate the application."""
        self.on_screen = ( -1, -1, -1, -1, -1, -1 )
        self._draw()
        wasp.system.request_event(wasp.EventMask.TOUCH |
                                  wasp.EventMask.SWIPE_UPDOWN |
                                  wasp.EventMask.BUTTON)

    def press(self, button, state):
        draw = wasp.watch.drawable
        if self.test == 'Button':
            draw.string('{}: {}'.format(button, state), 0, 108, width=240)
        elif self.test == 'Crash':
            self.crash()
        elif self.test == 'String':
            self._benchmark_string()
        elif self.test == 'Touch':
            draw.string('Button', 0, 108, width=240)

    def swipe(self, event):
        tests = self.tests
        i = tests.index(self.test)

        if event[0] == wasp.EventType.UP:
            i += 1
            if i >= len(tests):
                i = 0
        else:
            i -= 1
            if i < 0:
                i = len(tests) - 1
        self.test = tests[i]
        self._draw()

    def touch(self, event):
        if self.test == 'RLE':
            self._benchmark_rle()
        elif self.test == 'String':
            self._benchmark_string()
        elif self.test == 'Touch':
            wasp.watch.drawable.string('({}, {})'.format(
                    event[1], event[2]), 0, 108, width=240)
        elif self.test == 'Wrap':
            self._benchmark_wrap()

    def _benchmark_rle(self):
        draw = wasp.watch.drawable
        draw.fill(0, 0, 30, 240, 240-30)
        self.scroll.draw()
        t = machine.Timer(id=1, period=8000000)
        t.start()
        for i in range(0, 128, 16):
            draw.blit(self.ICON, i+16, i+32)
        elapsed = t.time()
        t.stop()
        del t
        draw.string('{}s'.format(elapsed / 1000000), 12, 24+192)

    def _benchmark_string(self):
        draw = wasp.watch.drawable
        draw.fill(0, 0, 30, 240, 240-30)
        self.scroll.draw()
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

    def _benchmark_wrap(self):
        draw = wasp.watch.drawable
        draw.fill(0, 0, 30, 240, 240-30)
        self.scroll.draw()
        t = machine.Timer(id=1, period=8000000)
        t.start()
        draw = wasp.watch.drawable
        s = 'This\nis a very long string that will need to be wrappedinmultipledifferentways!'
        chunks = draw.wrap(s, 240)

        for i in range(len(chunks)-1):
            sub = s[chunks[i]:chunks[i+1]].rstrip()
            draw.string(sub, 0, 48+24*i)
        elapsed = t.time()
        t.stop()
        del t
        draw.string('{}s'.format(elapsed / 1000000), 12, 24+192)

    def _draw(self):
        """Redraw the display from scratch."""
        wasp.watch.display.mute(True)
        draw = wasp.watch.drawable
        draw.fill()
        draw.string('{} test'.format(self.test),
                0, 6, width=240)
        self.scroll.draw()

        if self.test == 'Crash':
            draw.string("Press button to", 12, 24+24)
            draw.string("throw exception.", 12, 24+48)
        elif self.test == 'RLE':
            draw.blit(self.ICON, 120-48, 120-32)

        wasp.watch.display.mute(False)
