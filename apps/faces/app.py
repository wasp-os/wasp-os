# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 Daniel Thompson
"""Watch Face Chooser
~~~~~~~~~~~~~~~~~~~~~

A tool to select a suitable watch face.

.. figure:: res/screenshots/FacesApp.png
    :width: 179

The app is intended to be enabled by default and has, therefore, been carefully
structured to minimize memory usage when the app is not active.
"""

import wasp
import icons
import appregistry

class FacesApp():
    """Choose a default watch face."""
    NAME = 'Faces'
    ICON = icons.clock

    def foreground(self):
        """Activate the application."""
        choices = []
        for face in appregistry.faces_list:
            choices.append(face)

        self.choices = choices
        self.choice = 0
        self.si = wasp.widgets.ScrollIndicator()

        self._update()
        wasp.system.request_event(wasp.EventMask.SWIPE_UPDOWN)

    def background(self):
        self.choices = None
        del self.choices
        self.choice = None
        del self.choice
        self.si = None
        del self.si

        # When the watch face redraws then the change to the scrolling indicator
        # is a little subtle. Let's provide some haptic feedback too so the user
        # knows something has happened.
        wasp.watch.vibrator.pulse()

    def swipe(self, event):
        """Notify the application of a touchscreen swipe event."""
        choice = self.choice
        if event[0] == wasp.EventType.DOWN:
            choice = choice - 1 if choice > 0 else len(self.choices)-1
        if event[0] == wasp.EventType.UP:
            choice = choice + 1 if choice < len(self.choices)-1 else 0
        self.choice = choice

        mute = wasp.watch.display.mute
        mute(True)
        self._update()
        mute(False)

    def _update(self):
        """Draw the display from scratch."""
        wasp.watch.drawable.fill()
        (module, label) = self.choices[self.choice]
        wasp.system.register('{}.{}App'.format(module, label), watch_face=True)
        wasp.system.quick_ring[0].preview()
        self.si.draw()
