# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 Daniel Thompson
"""Software
~~~~~~~~~~~

A tool to enable/disable applications.

.. figure:: res/SoftwareApp.png
    :width: 179

Most applications are disabled by default at boot in order to conserve
RAM (which is in short supply and very useful to anyone wanting to
write an application). This tools allows us to boot and conserve RAM
whilst still allowing users to activate so many awesome applications!
"""

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
                ('play2048', wasp.widgets.Checkbox(0, 40, 'Play 2048')),
                ('snake', wasp.widgets.Checkbox(0, 80, 'Snake Game')),
                ('flashlight', wasp.widgets.Checkbox(0, 120, 'Torch')),
                ('testapp', wasp.widgets.Checkbox(0, 160, 'Test')),
                ('timer', wasp.widgets.Checkbox(0, 0, 'Timer')),
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
        pages = (len(self.db)-1) // 5
        if event[0] == wasp.EventType.DOWN:
            page = page - 1 if page > 0 else pages
        if event[0] == wasp.EventType.UP:
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
                    wasp.system.register('apps.{}.{}App'.format(module, label))
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
