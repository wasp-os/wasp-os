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

    # 2-bit RLE, generated from res/app_icon.png, 457 bytes
    RLE_2BIT = (
        96, 64,
        b'\x1e@md<d<d;f?X\xec2\xf0/'
        b'\xf2-\xf4,\xc3.\xc3,\xc3.\xc3,\xc3.\xc3,'
        b'\xc3.\xc3,\xc3.\xc3,\xc3\x0c\x80\xfc\x83\x10\xc0]'
        b'\xc3\x0c@\xffC,C\n\x87\x0c\xc7\nC,C\t'
        b'\x83\x02\x84\n\xc4\x02\xc3\tC,C\x08\x82\x07\x82\x08'
        b'\xc2\x07\xc2\x08C,C\x07\x82\t\x82\x06\xc2\t\xc2\x07'
        b'C,C\x06\x82\x0b\x82\x04\xc2\x0b\xc2\x06C,C\x06'
        b'\x82\x0b\x82\x04\xc2\x0b\xc2\x06C,C\x05\x82\x0c\x82\x04'
        b'\xc2\x0c\xc2\x05C,C\x05\x82\x0c\x82\x04\xc2\x0c\xc2\x05'
        b'C,C\x05\x83\x0b\x82\x04\xc2\x0b\xc3\x05C,C\x06'
        b'\x82\x0b\x82\x04\xc2\x0b\xc2\x06C,C\x06\x82\x0b\x82\x04'
        b'\xc2\x0b\xc1\x07C,C\x07\x82\n\x82\x04\xc2\n\xc2\x07'
        b'C+D\x08\x82\t\x82\x04\xc2\t\xc2\x08C*E\t'
        b'\x8c\x04\xcc\tC*E\n\x8b\x04\xcb\nC*E.'
        b'C*E.C*E.C*E.C*E\n'
        b'\x80\xe9\x8b\x04\xc0o\xcb\nC+D\t\x8c\x04\xcc\t'
        b'C,C\x08\x82\t\x82\x04\xc2\t\xc2\x08C,C\x07'
        b'\x82\n\x82\x04\xc2\n\xc2\x07C,C\x06\x82\x0b\x82\x04'
        b'\xc2\x0b\xc1\x07C,C\x06\x82\x0b\x82\x04\xc2\x0b\xc2\x06'
        b'C,C\x05\x83\x0b\x82\x04\xc2\x0b\xc3\x05C,C\x05'
        b'\x82\x0c\x82\x04\xc2\x0c\xc2\x05C,C\x05\x82\x0c\x82\x04'
        b'\xc2\x0c\xc2\x05C,C\x06\x82\x0b\x82\x04\xc2\x0b\xc2\x06'
        b'C,C\x06\x82\x0b\x82\x04\xc2\x0b\xc2\x06C,C\x07'
        b'\x82\t\x82\x06\xc2\t\xc2\x07C,C\x08\x82\x07\x82\x08'
        b'\xc2\x07\xc2\x08C,C\t\x83\x02\x84\n\xc4\x02\xc3\t'
        b'C,C\n\x86\x0e\xc6\nC,C\x0c\x83\x10\xc3\x0c'
        b'C,C.C,C.C,C.C,C.'
        b'C,C.C,t-r/p2l?X@'
        b'mf;d<d<d\x1e'
    )

    def __init__(self):
        self.tests = ('Touch', 'String', 'Button', 'Crash', '1-bit RLE', '2-bit RLE')
        self.test = self.tests[0]
        self.scroll = wasp.widgets.ScrollIndicator()

    def foreground(self):
        """Activate the application."""
        self.on_screen = ( -1, -1, -1, -1, -1, -1 )
        self.draw()
        wasp.system.request_event(wasp.EventMask.TOUCH |
                                  wasp.EventMask.SWIPE_UPDOWN |
                                  wasp.EventMask.BUTTON)

    def press(self, button, state):
        draw = wasp.watch.drawable
        if self.test == 'Touch':
            draw.string('Button', 0, 108, width=240)
        if self.test == 'String':
            self.benchmark_string()
        elif self.test == 'Button':
            draw.string('{}: {}'.format(button, state), 0, 108, width=240)
        elif self.test == 'Crash':
            self.crash()

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
        self.draw()

    def touch(self, event):
        if self.test == 'Touch':
            wasp.watch.drawable.string('({}, {})'.format(
                    event[1], event[2]), 0, 108, width=240)
        elif self.test == 'String':
            self.benchmark_string()
        elif self.test == '1-bit RLE':
            self.benchmark_rle_1bit()
        elif self.test == '2-bit RLE':
            self.benchmark_rle_2bit()

    def benchmark_rle_1bit(self):
        draw = wasp.watch.drawable
        draw.fill(0, 0, 30, 240, 240-30)
        self.scroll.draw()
        t = machine.Timer(id=1, period=8000000)
        t.start()
        for i in range(0, 128, 16):
            draw.rleblit(self.ICON, (i, 30 + i))
        elapsed = t.time()
        t.stop()
        del t
        draw.string('{}s'.format(elapsed / 1000000), 12, 24+192)

    def benchmark_rle_2bit(self):
        draw = wasp.watch.drawable
        draw.fill(0, 0, 30, 240, 240-30)
        self.scroll.draw()
        t = machine.Timer(id=1, period=8000000)
        t.start()
        for i in range(0, 128, 16):
            draw.rle2bit(self.RLE_2BIT, i, 30 + i)
        elapsed = t.time()
        t.stop()
        del t
        draw.string('{}s'.format(elapsed / 1000000), 12, 24+192)

    def benchmark_string(self):
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

    def draw(self):
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
        elif self.test == '1-bit RLE':
            draw.rleblit(self.ICON, (120-48, 120-32))
        elif self.test == '2-bit RLE':
            draw.rle2bit(self.RLE_2BIT, 120-48, 120-32)

        wasp.watch.display.mute(False)
