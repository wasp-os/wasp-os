# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 Daniel Thompson
"""Wizard to generate main.py."""

import wasp
import icons

class SoftwareApp():
    """Enable and disable applications."""
    NAME = 'Software'
    ICON = icons.software

    def foreground(self):
        """Activate the application."""
        self.db = (
                ('alarm', wasp.widgets.Checkbox(0, 0, 'Alarm')),
                ('calc', wasp.widgets.Checkbox(0, 40, 'Calculator')),
                ('chrono', wasp.widgets.Checkbox(0, 80, 'Chrono')),
                ('fibonacci_clock', wasp.widgets.Checkbox(0, 120, 'Fibonacci Clock')),
                ('gameoflife', wasp.widgets.Checkbox(0, 160, 'Game Of Life')),
                ('musicplayer', wasp.widgets.Checkbox(0, 0, 'Music Player')),
                ('snake', wasp.widgets.Checkbox(0, 40, 'Snake Game')),
                ('flashlight', wasp.widgets.Checkbox(0, 80, 'Torch')),
                ('testapp', wasp.widgets.Checkbox(0, 120, 'Test')),
            )
        self.si = wasp.widgets.ScrollIndicator()
        self.page = 0

        # Get the initial state for the checkboxes
        for _, checkbox in self.db:
            label = checkbox.label.replace(' ', '')
            for app in wasp.system.launcher_ring:
                if type(app).__name__.startswith(label):
                    checkbox.state = True
                    break

        self._draw()
        wasp.system.request_event(wasp.EventMask.TOUCH |
                                  wasp.EventMask.SWIPE_UPDOWN)

    def get_page(self):
        i = self.page * 5
        return self.db[i:i+5]

    def swipe(self, event):
        """Notify the application of a touchscreen swipe event."""
        page = self.page
        pages = 1
        if event[0] == wasp.EventType.UP:
            page = page - 1 if page > 0 else pages
        if event[0] == wasp.EventType.DOWN:
            page = page + 1 if page < pages else 0
        self.page = page

        mute = wasp.watch.display.mute
        mute(True)
        self._draw()
        mute(False)

    def touch(self, event):
        """Notify the application of a touchscreen touch event."""
        for module, checkbox in self.get_page():
            if checkbox.touch(event):
                label = checkbox.label.replace(' ', '')
                if checkbox.state:
                    exec('import apps.{}'.format(module))
                    exec('wasp.system.register(apps.{}.{}App())'.format(module, label))
                else:
                    for app in wasp.system.launcher_ring:
                        if type(app).__name__.startswith(label):
                            wasp.system.launcher_ring.remove(app)
                            break
                break

    def _draw(self):
        """Draw the display from scratch."""
        wasp.watch.drawable.fill()
        self.si.draw()
        for _, checkbox in self.get_page():
            checkbox.draw()
