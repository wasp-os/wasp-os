# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 Daniel Thompson

"""Self Tests
~~~~~~~~~~~~~

A collection of tests used to develop features or provide useful metrics such
as performance indicators or memory usage.

.. figure:: res/screenshots/TestApp.png
    :width: 179
"""

import wasp

import gc
import fonts
import icons
import machine

from apps.system.pager import PagerApp

class TestApp():
    """Self test application."""
    NAME = 'Self Test'
    ICON = icons.app

    def __init__(self):
        self.tests = ('Alarm', 'Button', 'Checkbox', 'Crash', 'Colours', 'Fill', 'Fill-H', 'Fill-V', 'Free Mem', 'Line', 'Notifications', 'RLE', 'String', 'Touch', 'Wrap')
        self.test = self.tests[0]
        self.scroll = wasp.widgets.ScrollIndicator()

        self._checkbox = wasp.widgets.Checkbox(4, 104, 'Check me')
        self._sliders = (
                wasp.widgets.Slider(32, 10, 90, 0xf800),
                wasp.widgets.Slider(64, 10, 140, 0x27e4),
                wasp.widgets.Slider(32, 10, 190, 0x211f),
        )
        self._spinner = wasp.widgets.Spinner(90, 60, 0, 99)

    def foreground(self):
        """Activate the application."""
        self.on_screen = ( -1, -1, -1, -1, -1, -1 )
        self._draw()
        wasp.system.request_event(wasp.EventMask.TOUCH |
                                  wasp.EventMask.SWIPE_UPDOWN |
                                  wasp.EventMask.BUTTON)

    def press(self, button, state):
        draw = wasp.watch.drawable
        if self.test == 'Alarm':
            self._test_alarm()
        elif self.test == 'Button':
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
        if self.test == 'Checkbox':
            self._checkbox.touch(event)
        elif self.test == 'Colours':
            if event[2] > 90:
                s = self._sliders[(event[2] - 90) // 50]
                s.touch(event)
                s.update()
                self.scroll.draw()
                self._update_colours()
        elif self.test.startswith('Fill'):
            self._benchmark_fill()
        elif self.test == 'Notifications':
            if self._spinner.touch(event):
                notifications = wasp.system.notifications

                if len(notifications) > self._spinner.value:
                    wasp.system.unnotify(
                            next(iter(notifications.keys())))
                else:
                    wasp.system.notify(wasp.watch.rtc.get_uptime_ms(),
                        {
                            "src":"Hangouts",
                            "title":"A Name",
                            "body":"message contents"
                        })
        elif self.test == 'RLE':
            self._benchmark_rle()
        elif self.test == 'String':
            self._benchmark_string()
        elif self.test == 'Touch':
            wasp.watch.drawable.string('({}, {})'.format(
                    event[1], event[2]), 0, 108, width=240)
        elif self.test == 'Wrap':
            self._benchmark_wrap()
        elif self.test == 'Line':
            self._benchmark_line()

    def _alarm(self):
        wasp.system.wake()
        wasp.system.switch(PagerApp('Alarm triggered'))

    def _test_alarm(self):
        def nop():
            pass
        now = wasp.watch.rtc.time()
        wasp.system.set_alarm(now + 30, self._alarm)
        wasp.system.set_alarm(now + 30, nop)
        if not wasp.system.cancel_alarm(now + 30, nop):
            bug()
        wasp.watch.drawable.string("Done.", 12, 24+80)

    def _benchmark_rle(self):
        draw = wasp.watch.drawable
        draw.fill(0, 0, 30, 240, 240-30)
        self.scroll.draw()
        t = machine.Timer(id=1, period=8000000)
        t.start()
        for i in range(0, 128, 16):
            draw.blit(icons.software, i+16, i+32)
        elapsed = t.time()
        t.stop()
        del t
        draw.string('{}s'.format(elapsed / 1000000), 12, 24+192)

    def _benchmark_fill(self):
        draw = wasp.watch.drawable
        draw.fill(0, 0, 30, 240, 240-30)
        self.scroll.draw()
        t = machine.Timer(id=1, period=8000000)
        if self.test == 'Fill':
            t.start()
            draw.fill(0xffff, 60, 60, 120, 120)
            elapsed = t.time()
        elif self.test == 'Fill-H':
            t.start()
            for i in range(60, 180, 2):
                draw.fill(0xffff, 60, i, 120, 1)
            elapsed = t.time()
        elif self.test == 'Fill-V':
            t.start()
            for i in range(60, 180, 2):
                draw.fill(0xffff, i, 60, 1, 120)
            elapsed = t.time()

        t.stop()
        del t
        draw.string('{}s'.format(elapsed / 1000000), 12, 24+192)

    def _benchmark_string(self):
        draw = wasp.watch.drawable
        draw.fill(0, 0, 30, 240, 240-30)
        draw.set_color(0xffff, 0x4208)
        self.scroll.draw()
        t = machine.Timer(id=1, period=8000000)
        t.start()
        draw.string("The quick brown", 12, 24+24)
        draw.string("fox jumped over", 12, 24+48)
        draw.string("the lazy dog.", 12, 24+72)
        draw.string("0123456789", 12, 24+120, width=228)
        draw.string('!"£$%^&*()', 12, 24+144, width=228)
        elapsed = t.time()
        t.stop()
        del t
        draw.string('{}s'.format(elapsed / 1000000), 12, 24+192)

    def _benchmark_line(self):
        draw = wasp.watch.drawable
        # instead of calculating by trig functions, use LUT
        points = (0, 50), (19, 46), (35, 35), (46, 19),

        draw.fill(0, 70, 70, 100, 100)
        self.scroll.draw()
        t = machine.Timer(id=1, period=8000000)
        t.start()
        for x, y in points:
            draw.line(120, 120, 120+x, 120+y, 4, 0xfb00)  # red
            draw.line(120, 120, 120+y, 120-x, 3, 0x07c0)  # green
            draw.line(120, 120, 120-x, 120-y, 5, 0x6b3f)  # blue
            draw.line(120, 120, 120-y, 120+x, 2, 0xffe0)  # yellow
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
        draw.set_font(fonts.sans24)
        draw.string('{} test'.format(self.test),
                0, 6, width=240)

        if self.test == 'Alarm':
            draw.string("Press button to", 12, 24+24)
            draw.string("set alarm.", 12, 24+48)
        elif self.test == 'Checkbox':
            self._checkbox.draw()
        elif self.test == 'Crash':
            draw.string("Press button to", 12, 24+24)
            draw.string("throw exception.", 12, 24+48)
        elif self.test == 'Colours':
            for s in self._sliders:
                s.draw()
            self._update_colours()
        elif self.test == 'Free Mem':
            if wasp.watch.free:
                draw.string("Boot: {}".format(wasp.watch.free), 12, 3*24)
                draw.string("Init: {}".format(wasp.free), 12, 4*24)
                draw.string("Now: {}".format(gc.mem_free()), 12, 5*24)
                gc.collect()
                draw.string("GC: {}".format(gc.mem_free()), 12, 6*24)
            else:
                draw.string("Not supported", 12, 4*24)
        elif self.test == 'Notifications':
            self._spinner.value = len(wasp.system.notifications)
            self._spinner.draw()
        elif self.test == 'RLE':
            draw.blit(self.ICON, 120-48, 120-32)

        self.scroll.draw()
        wasp.watch.display.mute(False)

    def _update_colours(self):
        draw = wasp.watch.drawable
        r = self._sliders[0].value
        g = self._sliders[1].value
        b = self._sliders[2].value
        rgb = (r << 11) + (g << 5) + b

        draw.string('RGB565 #{:04x}'.format(rgb), 0, 6, width=240)
        draw.fill(rgb, 60, 35, 120, 50)
