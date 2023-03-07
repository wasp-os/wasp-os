# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 Daniel Thompson
"""Software
~~~~~~~~~~~

A tool to enable/disable applications.

.. figure:: res/screenshots/SoftwareApp.png
    :width: 179

Most applications are disabled by default at boot in order to conserve
RAM (which is in short supply and very useful to anyone wanting to
write an application). This tools allows us to boot and conserve RAM
whilst still allowing users to activate so many awesome applications!
"""

import wasp
import icons
import os
import gc
import appregistry


class SoftwareApp():
    """Enable and disable applications."""
    NAME = 'Software'
    ICON = icons.software

    def foreground(self):
        """Activate the application."""

        def factory(label):
            nonlocal y

            cb = wasp.widgets.Checkbox(0, y, label)
            y += 40
            if y > 160:
                y = 0
            return cb

        y = 0
        db = []
        for app in appregistry.software_list:
          db.append((app[0], factory(app[1])))

        # Handle user-loaded applications
        try:
            for app in os.listdir('apps'):
                name = None
                if app.endswith('.py'):
                    name = app[:-3]
                if app.endswith('.mpy'):
                    name = app[:-4]
                if name:
                    # Don't add apps that already exist (prioritize frozen apps)
                    load = True
                    for db_app in db:
                        if db_app[0][db_app[0].rindex('.') + 1:] == name:
                           load = False
                           break
                    if load:
                        db.append(('apps.' + name, factory(self._snake_case_to_pascal_case(name))))
        except OSError:
            # apps does not exist...
            pass

        # Get the initial state for the checkboxes
        for _, checkbox in db:
            label = checkbox.label.replace(' ', '')
            for app in wasp.system.launcher_ring:
                if type(app).__name__.startswith(label):
                    checkbox.state = True
                    break

        self.si = wasp.widgets.ScrollIndicator()
        self.page = 0
        self.db = db

        self._draw()
        wasp.system.request_event(wasp.EventMask.TOUCH |
                                  wasp.EventMask.SWIPE_UPDOWN)

    def background(self):
        self.si = None
        del self.si
        self.page = None
        del self.page
        self.db = None
        del self.db

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
                    gc.collect()
                    wasp.system.register('{}.{}App'.format(module, label))
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

    @staticmethod
    def _snake_case_to_pascal_case(s):
        out = ''
        for word in s.split('_'):
            out = out + word[:1].upper() + word[1:]
        return out