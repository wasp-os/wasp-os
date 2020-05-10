# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 Daniel Thompson
"""The complete set of wasp-os application entry points are documented
below as part of a template application. Note that the template does
not rely on any specific parent class. This is because applications in
wasp-os can rely on *duck typing* making a class hierarchy pointless.
"""

import wasp
import icons

class TemplateApp():
    """Template application.

    The template application includes every application entry point. It
    is used as a reference guide and can also be used as a template for
    creating new applications.

    .. data:: NAME = 'Template'

       Applications must provide a short ``NAME`` that is used by the
       launcher to describe the application. Names that are longer than
       8 characters are likely to be abridged by the launcher in order
       to fit on the screen.

    .. data:: ICON = RLE2DATA

       Applications can optionally provide an icon for display by the
       launcher. Applications that expect to be installed on the quick
       ring will not be listed by the launcher and need not provide any
       icon. When no icon is provided the system will use a default
       icon.

       The icon is an opportunity to differentiate your application from others
       so supplying an icon is strongly recommended. The icon, when provided,
       must not be larger than 96x64.

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
