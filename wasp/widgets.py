# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 Daniel Thompson

"""Widget library
~~~~~~~~~~~~~~~~~

The widget library allows common fragments of logic and drawing code to be
shared between applications.
"""

import fonts
import icons
import wasp
import watch

from micropython import const

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
                draw.blit(icon, 239-icon[1], 0,
                             fg=wasp.system.theme('battery'))
                self.level = -1
        else:
            level = watch.battery.level()
            if level == self.level:
                return


            green = level // 3
            if green > 31:
                green = 31
            red = 31-green
            rgb = (red << 11) + (green << 6)

            if self.level < 0 or ((level > 5) ^ (self.level > 5)):
                if level  > 5:
                    draw.blit(icon, 239-icon[1], 0,
                             fg=wasp.system.theme('battery'))
                else:
                    rgb = 0xf800
                    draw.blit(icon, 239-icon[1], 0, fg=0xf800)

            w = icon[1] - 10
            x = 239 - 5 - w
            h = 2*level // 11
            if 18 - h:
                draw.fill(0, x, 9, w, 18 - h)
            if h:
                draw.fill(rgb, x, 27 - h, w, h)

            self.level = level

class Clock:
    """Small clock widget."""
    def __init__(self, enabled=True):
        self.on_screen = None
        self.enabled = enabled

    def draw(self):
        """Redraw the clock from scratch.

        The container is required to clear the canvas prior to the redraw
        and the clock is only drawn if it is enabled.
        """
        self.on_screen = None
        self.update()

    def update(self):
        """Update the clock widget if needed.

        This is a lazy update that only redraws if the time has changes
        since the last call *and* the clock is enabled.

        :returns: An time tuple if the time has changed since the last call,
                  None otherwise.
        """
        now = wasp.watch.rtc.get_localtime()
        on_screen = self.on_screen

        if on_screen and on_screen == now:
            return None

        if self.enabled and (not on_screen
                or now[4] != on_screen[4] or now[3] != on_screen[3]):
            t1 = '{:02}:{:02}'.format(now[3], now[4])

            draw = wasp.watch.drawable
            draw.set_font(fonts.sans28)
            draw.set_color(wasp.system.theme('status-clock'))
            draw.string(t1, 52, 4, 138)

        self.on_screen = now
        return now

class NotificationBar:
    """Show BT status and if there are pending notifications."""
    def __init__(self, x=0, y=0):
        self._pos = (x, y)

    def draw(self):
        """Redraw the notification widget.

        For this simple widget :py:meth:`~.draw` is simply a synonym for
        :py:meth:`~.update` because we unconditionally update from scratch.
        """
        self.update()

    def update(self):
        """Update the widget.

        This widget does not implement lazy redraw internally since this
        can often be implemented (with less state) by the container.
        """
        draw = watch.drawable
        (x, y) = self._pos

        if wasp.watch.connected():
            draw.blit(icons.blestatus, x, y, fg=wasp.system.theme('ble'))
            if wasp.system.notifications:
                draw.blit(icons.notification, x+22, y,
                          fg=wasp.system.theme('notify-icon'))
            else:
                draw.fill(0, x+22, y, 30, 32)
        elif wasp.system.notifications:
            draw.blit(icons.notification, x, y,
                      fg=wasp.system.theme('notify-icon'))
            draw.fill(0, x+30, y, 22, 32)
        else:
            draw.fill(0, x, y, 52, 32)

class StatusBar:
    """Combo widget to handle notification, time and battery level."""
    def __init__(self):
        self._clock = Clock()
        self._meter = BatteryMeter()
        self._notif = NotificationBar()

    @property
    def clock(self):
        """True if the clock should be included in the status bar, False
        otherwise.
        """
        return self._clock.enabled

    @clock.setter
    def clock(self, enabled):
        self._clock.enabled = enabled

    def draw(self):
        """Redraw the status bar from scratch."""
        self._clock.draw()
        self._meter.draw()
        self._notif.draw()

    def update(self):
        """Lazily update the status bar.

        :returns: An time tuple if the time has changed since the last call,
                  None otherwise.
        """
        now = self._clock.update()
        if now:
            self._meter.update()
            self._notif.update()
        return now

class ScrollIndicator:
    """Scrolling indicator.

    A pair of arrows that prompted the user to swipe up/down to access
    additional pages of information.
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
        color = wasp.system.theme('scroll-indicator')

        if self.up:
            draw.blit(icons.up_arrow, self._pos[0], self._pos[1], fg=color)
        if self.down:
            draw.blit(icons.down_arrow, self._pos[0], self._pos[1]+13, fg=color)

_SLIDER_KNOB_DIAMETER = const(40)
_SLIDER_KNOB_RADIUS = const(_SLIDER_KNOB_DIAMETER // 2)
_SLIDER_WIDTH = const(220)
_SLIDER_TRACK = const(_SLIDER_WIDTH - _SLIDER_KNOB_DIAMETER)
_SLIDER_TRACK_HEIGHT = const(8)
_SLIDER_TRACK_Y1 = const(_SLIDER_KNOB_RADIUS - (_SLIDER_TRACK_HEIGHT // 2))
_SLIDER_TRACK_Y2 = const(_SLIDER_TRACK_Y1 + _SLIDER_TRACK_HEIGHT)

class Slider():
    """A slider to select values."""
    def __init__(self, steps, x=10, y=90, color=None):
        self.value = 0
        self._steps = steps
        self._stepsize = _SLIDER_TRACK / (steps-1)
        self._x = x
        self._y = y
        self._color = color
        self._lowlight = None

    def draw(self):
        """Draw the slider."""
        draw = watch.drawable
        x = self._x
        y = self._y
        color = self._color
        if self._color is None:
            self._color = wasp.system.theme('slider-default')
            color = self._color
        if self._lowlight is None:
            # Automatically generate a lowlight color
            if color < 0b10110_000000_00000:
                color = (color | 0b10110_000000_00000) & 0b10110_111111_11111
            if (color & 0b111111_00000) < 0b101100_00000:
                color = (color | 0b101100_00000) & 0b11111_101100_11111
            if (color & 0b11111) < 0b10110:
                color = (color | 0b11000) & 0b11111_111111_10110
            self._lowlight = color
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


_message_string_x_coord = const(0)
_message_string_y_coord = const(60)
_yes_button_x_coord = const(20)
_yes_button_y_coord = const(100)
_no_button_x_coord = const(120)
_no_button_y_coord = const(100)

class ConfirmationView:
    "Confirmation widget allowing user confirmation of a setting"

    def __init__(self):
        self.active = False

        self.yes_button_bounds = (
            (_yes_button_x_coord, _yes_button_y_coord),
            (
                icons.yes_button[0] + _yes_button_x_coord,
                icons.yes_button[1] + _yes_button_y_coord,
            ),
        )
        self.no_button_bounds = (
            (_no_button_x_coord, _no_button_y_coord),
            (
                icons.no_button[0] + _no_button_x_coord,
                icons.no_button[1] + _no_button_y_coord,
            )
        )

    def draw(self, message):
        wasp.watch.drawable.fill(1)
        wasp.watch.drawable.string(
            message,
            _message_string_x_coord,
            _message_string_y_coord
        )
        wasp.watch.drawable.blit(
            icons.yes_button,
            _yes_button_x_coord,
            _yes_button_y_coord,
        )
        wasp.watch.drawable.blit(
            icons.no_button,
            _no_button_x_coord,
            _no_button_y_coord,
        )
        self.active = True


    def touch(self, event):
        x_coord = event[1]
        y_coord = event[2]
        is_yes_button_press = (
            x_coord > self.yes_button_bounds[0][0]
            and y_coord > self.yes_button_bounds[0][1]
            and x_coord < self.yes_button_bounds[1][0]
            and y_coord < self.yes_button_bounds[1][1]
        )

        is_no_button_press = (
            x_coord > self.no_button_bounds[0][0]
            and y_coord > self.no_button_bounds[0][1]
            and x_coord < self.no_button_bounds[1][0]
            and y_coord < self.no_button_bounds[1][1]
        )

        if is_yes_button_press:
            self.active = False
            return True
        elif is_no_button_press:
            self.active = False
            return False
        else:
            return None
