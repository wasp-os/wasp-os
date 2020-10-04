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
        self.pages = ('Brightness', 'Launcher Colors')
        self.page = 0
        self._slider = wasp.widgets.Slider(3, 10, 90)
        self._color_sliders = (
            wasp.widgets.Slider(32, 10, 90, 0xf800),
            wasp.widgets.Slider(64, 10, 140, 0x27e4),
            wasp.widgets.Slider(32, 10, 190, 0x211f),
        )

    def foreground(self):
        self._draw()
        wasp.system.request_event(wasp.EventMask.TOUCH |
                                  wasp.EventMask.SWIPE_UPDOWN)

    def touch(self, event):
        if self.pages[self.page] == 'Brightness':
            self._slider.touch(event)
            wasp.system.brightness = self._slider.value + 1
        elif self.pages[self.page] == 'Launcher Colors':
            if event[2] > 90:
                self._color_sliders[(event[2]-90) // 50].touch(event)
        self._update()

    def swipe(self, event):
        if event[0] == wasp.EventType.UP:
            self.page += 1
            if self.page >= len(self.pages):
                self.page = 0
        else:
            self.page -= 1
            if self.page < 0:
                self.page = len(self.pages) - 1
        self._draw()

    def _draw(self):
        """Redraw the display from scratch."""
        wasp.watch.drawable.fill()
        wasp.watch.drawable.string(self.pages[self.page], 0, 6, width=240)
        if self.pages[self.page] == 'Brightness':
            self._slider.draw()
        elif self.pages[self.page] == 'Launcher Colors':
            for slider in self._color_sliders:
                slider.draw()
        self._update()

    def _update(self):
        if self.pages[self.page] == 'Brightness':
            if wasp.system.brightness == 3:
                say = "High"
            elif wasp.system.brightness == 2:
                say = "Mid"
            else:
                say = "Low"
            wasp.watch.drawable.string(say, 0, 150, width=240)
            self._slider.update()
            # self._slider.draw()
        elif self.pages[self.page] == 'Launcher Colors':
            for slider in self._color_sliders:
                slider.update()
            r = self._color_sliders[0].value
            g = self._color_sliders[1].value
            b = self._color_sliders[2].value
            rgb = (r << 11) + (g << 5) + b
            wasp.system.launcher_border_color = rgb
