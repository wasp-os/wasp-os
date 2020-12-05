# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 Daniel Thompson

import wasp
import icons

class SettingsApp():
    """Ultra-simple settings application.

    Currently the settings application contains only one setting: brightness

    .. figure:: res/SettingsApp.png
        :width: 179

        Screenshot of the settings application
    """
    NAME = 'Settings'
    ICON = icons.settings

    def __init__(self):
        self._slider = wasp.widgets.Slider(3, 10, 90)
        self._nfy_slider = wasp.widgets.Slider(3, 10, 90)
        self._scroll_indicator = wasp.widgets.ScrollIndicator()
        self._settings = ['Brightness', 'Notification Level']
        self._sett_index = 0
        self._current_setting = self._settings[0]

    def foreground(self):
        self._slider.value = wasp.system.brightness - 1
        self._draw()
        wasp.system.request_event(wasp.EventMask.TOUCH)
        wasp.system.request_event(wasp.EventMask.SWIPE_UPDOWN)

    def touch(self, event):
        if self._current_setting == 'Brightness':
            self._slider.touch(event)
            wasp.system.brightness = self._slider.value + 1
        elif self._current_setting == 'Notification Level':
            self._nfy_slider.touch(event)
            wasp.system.notify_level = self._nfy_slider.value + 1
        self._update()

    def swipe(self, event):
        """Handle NEXT events by augmenting the default processing by resetting
        the count if we are not currently timing something.

        No other swipe event is possible for this application.
        """
        if event[0] == wasp.EventType.UP:
            self._sett_index += 1
            self._draw()
        elif event[0] == wasp.EventType.DOWN:
            self._sett_index -= 1
            self._draw()

    def _draw(self):
        """Redraw the display from scratch."""
        self._current_setting = self._settings[self._sett_index % len(self._settings)]
        wasp.watch.drawable.fill()
        wasp.watch.drawable.string(self._current_setting, 0, 6, width=240)
        if self._current_setting == 'Brightness':
            self._slider.value = wasp.system.brightness - 1
        elif self._current_setting == 'Notification Level':
            self._nfy_slider.value = wasp.system.notify_level - 1
        self._update()

    def _update(self):
        if self._current_setting == 'Brightness':
            if wasp.system.brightness == 3:
                say = "High"
            elif wasp.system.brightness == 2:
                say = "Mid"
            else:
                say = "Low"
            self._slider.update()
        elif self._current_setting == 'Notification Level':
            if wasp.system.notify_level == 3:
                say = "High"
            elif wasp.system.notify_level == 2:
                say = "Mid"
            else:
                say = "Silent"
            self._nfy_slider.update()
        wasp.watch.drawable.string(say, 0, 150, width=240)
        self._scroll_indicator.draw()
