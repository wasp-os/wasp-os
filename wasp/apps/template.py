# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 Daniel Thompson

import wasp
import icons

class TemplateApp():
    """Template application ready to use as a basis for new applications.
    """
    NAME = 'Template'
    ICON = icons.app

    def __init__(self):
        pass

    def foreground(self):
        """Activate the application."""
        self._draw()
        wasp.system.request_event(wasp.EventMask.TOUCH |
                                  wasp.EventMask.SWIPE_UPDOWN |
                                  wasp.EventMask.BUTTON)

    def press(self, button, state):
        draw = wasp.watch.drawable
        draw.string('Button', 0, 108, width=240)

    def swipe(self, event):
        draw = wasp.watch.drawable
        if event[0] == wasp.EventType.UP:
            draw.string('Swipe up', 0, 108, width=240)
        else:
            draw.string('Swipe down', 0, 108, width=240)

    def touch(self, event):
        draw = wasp.watch.drawable
        wasp.watch.drawable.string('({}, {})'.format(
                event[1], event[2]), 0, 108, width=240)

    def _draw(self):
        """Draw the display from scratch."""
        draw = wasp.watch.drawable
        draw.fill()
        draw.string('Template', 0, 6, width=240)
