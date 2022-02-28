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
        """Called when the application is launched, for example by pressing
        its icon."""
        self._draw()
        wasp.system.request_event(wasp.EventMask.TOUCH |
                                  wasp.EventMask.SWIPE_UPDOWN |
                                  wasp.EventMask.BUTTON)
        wasp.system.request_tick(1000)

    def background(self):
        """Called when the leaving the application, either because of screen
        timeout of directly by the user."""
        pass

    def sleep(self):
        """Called by the system to notify the application that the screen is
        about to be turned off. Most apps should not implement it.
        If not implemented or returning True: goes back to the default clock
        application. If implemented and returning False: turning the screen
        back on will show the current application"""
        return False

    def wake(self):
        """Notify the application that the screen is waking up. Generally used
        to redraw the screen or to re-enable ticks."""
        pass

    def preview(self):
        """Provide a preview for the watch face selection.

        preview() must be implemented by watch face applications because it
        is called by the watch face selector. When called the application should
        redraw the screen as through it was the foreground() application. The
        application will not be active after the preview.

        Other applications should not implement this entry point.
        """
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
        """Notify the application that a periodic tick is due. Note that
        ticks are not called when watch is sleeping (i.e. screen is off)."""
        pass

    def touch(self, event):
        """Notify the application of a touchscreen touch event."""
        draw = wasp.watch.drawable
        wasp.watch.drawable.string('({}, {})'.format(
                event[1], event[2]), 0, 108, width=240)

    def _draw(self):
        """Draw or redraw the entirety of the display."""
        draw = wasp.watch.drawable
        draw.fill()
        draw.string(self.NAME, 0, 6, width=240)
        self._update()

    def _update(self):
        """Draw a specific part of the display. Usually used to update only the
        dynamic parts of the application display."""
        pass
