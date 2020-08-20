# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 Daniel Thompson

"""Widget library
~~~~~~~~~~~~~~~~~

The widget library allows common fragments of logic and drawing code to be
shared between applications.
"""

import icons
import wasp
import watch
from micropython import const

# 1-bit RLE, generated from res/vbattery_charging.png, 147 bytes
vbattery_charging = (
    48, 36,
    b'\xff\x00\x89$\x0c$\x0c$\x0c$\n\x06\x1c\x04\t\x07'
    b'\x1c\x04\t\x07\n\x04\x0e\x04\x08\x08\n\x05\r\x04\x08\x04'
    b'\x06\x04\x04\x06\x0c\x04\x08\x04\x06\x05\x03\x07\x0b\x04\x08\x04'
    b'\x06\x06\x02\x08\n\x04\x08\x04\x06\x07\x01\t\t\x04\x08\x04'
    b'\x07\x11\x08\x04\x08\x04\x08\x11\x07\x04\x08\x04\t\x11\x06\x04'
    b'\x08\x04\n\x11\x05\x04\x08\x04\x0b\t\x01\x07\x04\x04\x08\x04'
    b'\x0c\x08\x02\x06\x04\x04\x08\x04\r\x07\x03\x05\x04\x04\x08\x04'
    b'\x0e\x06\x04\x04\x04\x04\x08\x08\x0b\x05\x0c\x04\t\x07\x0c\x04'
    b'\x0c\x04\t\x07\x1c\x04\n\x06\x1c\x04\x0c$\x0c$\x0c$'
    b'\x0c$\x04')

class BatteryMeter:
    """Battery meter widget.

    A simple battery meter with a charging indicator, will draw at the
    top-right of the display.
    """
    def __init__(self):
        self.level = -2

    def draw(self):
        """Draw from meter (from scratch)."""
        self.level = -2
        self.update()

    def update(self):
        """Update the meter.

        The update is lazy and won't redraw unless the level has changed.
        """
        icon = icons.battery
        draw = watch.drawable

        if watch.battery.charging():
            if self.level != -1:
                draw.rleblit(icon, pos=(239-icon[0], 0), fg=0x7bef)
                self.level = -1
        else:
            level = watch.battery.level()
            if level == self.level:
                return

            if level > 96:
                h = 24
                rgb = 0x07e0
            else:
                h = level // 4

                green = level // 3
                red = 31-green
                rgb = (red << 11) + (green << 6)

            if (level > 5) ^ (self.level > 5):
                if level  > 5:
                    draw.rleblit(icon, pos=(239-icon[0], 0), fg=0x7bef)
                else:
                    rgb = 0xf800
                    draw.rleblit(icon, pos=(239-icon[0], 0), fg=0xf800)

            x = 239 - 30
            w = 16
            if 24 - h:
                draw.fill(0, x, 14, w, 24 - h)
            if h:
                draw.fill(rgb, x, 38 - h, w, h)

            self.level = level

green, red = 0x07e0, 0xf800

class VerticalBatteryMeter(object):
    def __init__(self):
        self.level = -2

    def draw(self):
        self.level = -2
        self.update()

    def update(self):
        icon = vbattery_charging
        draw = watch.drawable
    
        if watch.battery.charging():
            if self.level != -1:
                draw.rleblit(icon, pos=(239-icon[0], 0), fg=0xe73c)
                self.level = -1
        else:
            level = watch.battery.level()
            if ((level <= (self.level + 4)) and (level >= (self.level - 5))):
                return

            if level <= 8:
                draw.rleblit(icon, pos=(239-icon[0], 0), fg= red)
                draw.fill(0, 203, 14, 26, 17)
                return

            draw.rleblit(icon, pos=(239-icon[0], 0), fg=0xe73c)
            draw.fill(0, 203, 14, 26, 17)
            width = (level // 7 )*2
            draw.fill(green, 205 + (25-width), 13, width, 17)


            self.level = level


class StatusBar:
    """Show BT status and if there are pending notifications."""
    def __init__(self, x=8, y=8):
        self._pos = (x, y)

    def draw(self):
        """Update the notification widget.

        For this simple widget :py:meth:`~.draw` is simply a synonym for
        :py:meth:`~.update`.
        """
        self.update()

    def update(self):
        """Update the widget.
        """
        draw = watch.drawable
        (x, y) = self._pos

        if wasp.watch.connected():
            draw.blit(icons.blestatus, x, y, fg=0x7bef)
            if wasp.system.notifications:
                draw.blit(icons.notification, x+24, y, fg=0x7bef)
            else:
                draw.fill(0, x+24, y, 32, 32)
        elif wasp.system.notifications:
            draw.blit(icons.notification, x, y, fg=0x7bef)
            draw.fill(0, x+32, y, 32, 32)
        else:
            draw.fill(0, x, y, 56, 32)

class ScrollIndicator:
    """Scrolling indicator.

    A simple battery meter with a charging indicator, will draw at the
    top-right of the display.
    """
    def __init__(self, x=240-18, y=240-24):
        self._pos = (x, y)
        self.up = True
        self.down = True

    def draw(self):
        """Draw from scrolling indicator.

        For this simple widget :py:meth:`~.draw` is simply a synonym for
        :py:meth:`~.update`.
        """
        self.update()

    def update(self):
        """Update from scrolling indicator."""
        draw = watch.drawable
        if self.up:
            draw.rleblit(icons.up_arrow, pos=self._pos, fg=0x7bef)
        if self.down:
            draw.rleblit(icons.down_arrow, pos=(self._pos[0], self._pos[1] + 13), fg=0x7bef)

_SLIDER_KNOB_DIAMETER = const(40)
_SLIDER_KNOB_RADIUS = const(_SLIDER_KNOB_DIAMETER // 2)
_SLIDER_WIDTH = const(220)
_SLIDER_TRACK = const(_SLIDER_WIDTH - _SLIDER_KNOB_DIAMETER)
_SLIDER_TRACK_HEIGHT = const(8)
_SLIDER_TRACK_Y1 = const(_SLIDER_KNOB_RADIUS - (_SLIDER_TRACK_HEIGHT // 2))
_SLIDER_TRACK_Y2 = const(_SLIDER_TRACK_Y1 + _SLIDER_TRACK_HEIGHT)

class Slider():
    """A slider to select values."""
    def __init__(self, steps, x=10, y=90, color=0x39ff):
        self.value = 0
        self._steps = steps
        self._stepsize = _SLIDER_TRACK / (steps-1)
        self._x = x
        self._y = y
        self._color = color

        # Automatically generate a lowlight color
        if color < 0b10110_000000_00000:
            color = (color | 0b10110_000000_00000) & 0b10110_111111_11111
        if (color & 0b111111_00000) < 0b101100_00000:
            color = (color | 0b101100_00000) & 0b11111_101100_11111
        if (color & 0b11111) < 0b10110:
            color = (color | 0b11000) & 0b11111_111111_10110
        self._lowlight = color

    def draw(self):
        """Draw the slider."""
        draw = watch.drawable
        x = self._x
        y = self._y
        color = self._color
        light = self._lowlight

        knob_x = x + ((_SLIDER_TRACK * self.value) // (self._steps-1))
        draw.blit(icons.knob, knob_x, y, color)

        w = knob_x - x
        if w > 0:
            draw.fill(0, x, y, w, _SLIDER_TRACK_Y1)
            if w > _SLIDER_KNOB_RADIUS:
                draw.fill(0, x, y+_SLIDER_TRACK_Y1,
                          _SLIDER_KNOB_RADIUS, _SLIDER_TRACK_HEIGHT)
                draw.fill(color, x+_SLIDER_KNOB_RADIUS, y+_SLIDER_TRACK_Y1,
                          w-_SLIDER_KNOB_RADIUS, _SLIDER_TRACK_HEIGHT)
            else:
                draw.fill(0, x, y+_SLIDER_TRACK_Y1, w, _SLIDER_TRACK_HEIGHT)
            draw.fill(0, x, y+_SLIDER_TRACK_Y2, w, _SLIDER_TRACK_Y1)

        sx = knob_x + _SLIDER_KNOB_DIAMETER
        w = _SLIDER_WIDTH - _SLIDER_KNOB_DIAMETER - w
        if w > 0:
            draw.fill(0, sx, y, w, _SLIDER_TRACK_Y1)
            if w > _SLIDER_KNOB_RADIUS:
                draw.fill(0, sx+w-_SLIDER_KNOB_RADIUS, y+_SLIDER_TRACK_Y1,
                          _SLIDER_KNOB_RADIUS, _SLIDER_TRACK_HEIGHT)
                draw.fill(light, sx, y+_SLIDER_TRACK_Y1,
                          w-_SLIDER_KNOB_RADIUS, _SLIDER_TRACK_HEIGHT)
            else:
                draw.fill(0, sx, y+_SLIDER_TRACK_Y1, w, _SLIDER_TRACK_HEIGHT)
            draw.fill(0, sx, y+_SLIDER_TRACK_Y2, w, _SLIDER_TRACK_Y1)

    def update(self):
        self.draw()

    def touch(self, event):
        tx = event[1]
        threshold = self._x + 20 - (self._stepsize / 2)
        v = int((tx - threshold) / self._stepsize)
        if v < 0:
            v = 0
        elif v >= self._steps:
            v = self._steps - 1
        self.value = v
