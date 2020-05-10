# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 Daniel Thompson
"""Template application implementing all application method calls.
"""

import wasp
import icons

class TemplateApp():
    """Template application ready to use as a basis for new applications.
    """
    NAME = 'Template'
    ICON = icons.app

    def __init__(self):
        """Initialize the application."""
        pass

    def foreground(self):
        """Activate the application."""
        self._draw()
        wasp.system.request_event(wasp.EventMask.TOUCH |
                                  wasp.EventMask.SWIPE_UPDOWN |
                                  wasp.EventMask.BUTTON)
        wasp.system.request_tick(1000)

    def background(self):
        """De-activate the application."""
        pass

    def sleep(self):
        """Notify the application the device is about to sleep."""
        return False

    def wake(self):
        """Notify the application the device is waking up."""
        pass

    def press(self, button, state):
        """Notify the application of a button-press event."""
        draw = wasp.watch.drawable
        draw.string('Button', 0, 108, width=240)

    def swipe(self, event):
        """Notify the application of a touchscreen swipe event."""
        draw = wasp.watch.drawable
        if event[0] == wasp.EventType.UP:
            draw.string('Swipe up', 0, 108, width=240)
        else:
            draw.string('Swipe down', 0, 108, width=240)

    def tick(self, ticks):
        """Notify the application that its periodic tick is due."""
        pass

    def touch(self, event):
        """Notify the application of a touchscreen touch event."""
        draw = wasp.watch.drawable
        wasp.watch.drawable.string('({}, {})'.format(
                event[1], event[2]), 0, 108, width=240)

    def _draw(self):
        """Draw the display from scratch."""
        draw = wasp.watch.drawable
        draw.fill()
        draw.string(self.NAME, 0, 6, width=240)
        self._update()

    def _update(self):
        """Update the dynamic parts of the application display."""
        pass
