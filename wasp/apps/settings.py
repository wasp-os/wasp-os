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

    def foreground(self):
        self._draw()
        wasp.system.request_event(wasp.EventMask.TOUCH)

    def touch(self, event):
        self._slider.touch(event)
        wasp.system.brightness = self._slider.value + 1
        self._update()

    def _draw(self):
        """Redraw the display from scratch."""
        wasp.watch.drawable.fill()
        wasp.watch.drawable.string('Brightness', 0, 6, width=240)
        self._update()

    def _update(self):
        if wasp.system.brightness == 3:
            say = "High"
        elif wasp.system.brightness == 2:
            say = "Mid"
        else:
            say = "Low"
        wasp.watch.drawable.string(say, 0, 150, width=240)
        self._slider.update()
