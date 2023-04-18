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

class Button():
    """A button with a text label."""
    def __init__(self, x, y, w, h, label):
        self._im = (x, y, w, h, label)

    def draw(self):
        """Draw the button."""
        bg = wasp.watch.drawable.darken(wasp.system.theme('ui'))
        frame = wasp.system.theme('mid')
        txt = wasp.system.theme('bright')
        self.update(bg, frame, txt)

    def update(self, bg, frame, txt):
        draw = wasp.watch.drawable
        im = self._im

        draw.fill(bg, im[0], im[1], im[2], im[3])
        draw.set_color(txt, bg)
        draw.set_font(fonts.sans24)
        draw.string(im[4], im[0], im[1]+(im[3]//2)-12, width=im[2])

        draw.fill(frame, im[0],im[1],          im[2], 2)
        draw.fill(frame, im[0], im[1]+im[3]-2, im[2], 2)
        draw.fill(frame, im[0],         im[1], 2, im[3])
        draw.fill(frame, im[0]+im[2]-2, im[1], 2, im[3])

    def touch(self, event):
        """Handle touch events."""
        x = event[1]
        y = event[2]

        # Adopt a slightly oversized hit box
        im = self._im
        x1 = im[0] - 10
        x2 = x1 + im[2] + 20
        y1 = im[1] - 10
        y2 = y1 + im[3] + 20

        if x >= x1 and x < x2 and y >= y1 and y < y2:
            return True

        return False

class ToggleButton(Button):
    """A button with a text label that can be toggled on and off."""
    def __init__(self, x, y, w, h, label):
        super().__init__(x, y, w, h, label)
        self.state = False

    def draw(self):
        """Draw the button."""
        draw = wasp.watch.drawable

        if self.state:
            bg = draw.darken(wasp.system.theme('ui'))
        else:
            bg = draw.darken(wasp.system.theme('mid'))
        frame = wasp.system.theme('mid')
        txt = wasp.system.theme('bright')

        self.update(bg, frame, txt)

    def touch(self, event):
        """Handle touch events."""
        if super().touch(event):
            self.state = not self.state
            self.draw()
            return True
        else:
            return False

class Checkbox():
    """A simple (labelled) checkbox."""
    def __init__(self, x, y, label=None):
        self._im = (x, y, label)
        self.state = False

    @property
    def label(self):
        return self._im[2]

    def draw(self):
        """Draw the checkbox and label."""
        draw = wasp.watch.drawable
        im = self._im
        if im[2]:
            draw.set_color(wasp.system.theme('bright'))
            draw.set_font(fonts.sans24)
            draw.string(im[2], im[0], im[1]+6)
        self.update()

    def update(self):
        """Draw the checkbox."""
        draw = wasp.watch.drawable
        im = self._im
        if self.state:
            c1 = wasp.system.theme('ui')
            c2 = draw.lighten(c1, wasp.system.theme('contrast'))
            fg = c2
        else:
            c1 = 0
            c2 = 0
            fg = wasp.system.theme('mid')
        # Draw checkbox on the right margin if there is a label, otherwise
        # draw at the natural location
        x = 239 - 32 - 4 if im[2] else im[0]
        draw.blit(icons.checkbox, x, im[1], fg, c1, c2)

    def touch(self, event):
        """Handle touch events."""
        x = event[1]
        y = event[2]
        im = self._im
        if (self.label or im[0] <= x < im[0]+40) and im[1] <= y < im[1]+40:
            self.state = not self.state
            self.update()
            return True
        return False

class GfxButton():
    """A button with a graphical icon."""
    def __init__(self, x, y, gfx):
        self._im = bytes((x, y))
        self.gfx = gfx

    def draw(self):
        """Draw the button."""
        im = self._im
        wasp.watch.drawable.blit(self.gfx, im[0], im[1])

    def touch(self, event):
        x = event[1]
        y = event[2]

        # Adopt a slightly oversized hit box
        im = self._im
        gfx = self.gfx
        x1 = im[0] - 10
        x2 = x1 + gfx[1] + 20
        y1 = im[1] - 10
        y2 = y1 + gfx[2] + 20

        if x >= x1 and x < x2 and y >= y1 and y < y2:
            return True

        return False

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
            self._color = wasp.system.theme('ui')
            color = self._color
        if self._lowlight is None:
            self._lowlight = draw.lighten(color, wasp.system.theme('contrast'))
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
        changed = self.value != v
        self.value = v
        return changed

class Spinner():
    """A simple Spinner widget.

    In order to have large enough hit boxes the spinner is a fairly large
    widget and requires 60x120 px.
    """
    def __init__(self, x, y, mn, mx, field=1, incr=1):
        self._im = bytes((x, y, mn, mx, field, incr))
        self.value = mn

    def draw(self):
        """Draw the spinner."""
        draw = watch.drawable
        im = self._im
        fg = draw.lighten(wasp.system.theme('ui'), wasp.system.theme('contrast'))
        draw.blit(icons.up_arrow, im[0]+30-8, im[1]+20, fg)
        draw.blit(icons.down_arrow, im[0]+30-8, im[1]+120-20-9, fg)
        self.update()

    def update(self):
        """Update the spinner value."""
        draw = watch.drawable
        im = self._im
        draw.set_color(wasp.system.theme('bright'))
        draw.set_font(fonts.sans28)
        s = str(self.value)
        if len(s) < im[4]:
            s = '0' * (im[4] - len(s)) + s
        draw.string(s, im[0], im[1]+60-14, width=60)

    def touch(self, event):
        x = event[1]
        y = event[2]
        im = self._im
        if x >= im[0] and x < im[0]+60 and y >= im[1] and y < im[1]+120:
            if y < im[1] + 60:
                self.value += im[5]
                if self.value > im[3]:
                    self.value = im[2]
            else:
                self.value -= im[5]
                if self.value < im[2]:
                    self.value = im[3]
            while self.value % im[5] != 0:
                self.value -= 1

            self.update()
            return True

        return False

class Stopwatch:
    """A stopwatch widget"""
    def __init__(self, y):
        self._y = y
        self.reset()

    def start(self):
        uptime = wasp.watch.rtc.get_uptime_ms() // 10
        self._started_at = uptime - self.count

    def stop(self):
        self._started_at = 0

    @property
    def started(self):
        return bool(self._started_at)

    def reset(self):
        self.count = 0
        self._started_at = 0
        self._last_count = -1

    def draw(self):
        self._last_count = -1
        self.update()

    def update(self):
        # Before we do anything else let's make sure count is
        # up to date
        if self._started_at:
            uptime = wasp.watch.rtc.get_uptime_ms() // 10
            self.count = uptime - self._started_at
            if self.count > 999*60*100:
                self.reset()

        if self._last_count != self.count:
            centisecs = self.count
            secs = centisecs // 100
            centisecs %= 100
            minutes = secs // 60
            secs %= 60

            t1 = '{}:{:02}'.format(minutes, secs)
            t2 = '{:02}'.format(centisecs)

            y = self._y
            draw = wasp.watch.drawable
            draw.set_font(fonts.sans36)
            draw.set_color(draw.lighten(wasp.system.theme('ui'), wasp.system.theme('contrast')))
            w = fonts.width(fonts.sans36, t1)
            draw.string(t1, 180-w, y)
            draw.fill(0, 0, y, 180-w, 36)
            draw.set_font(fonts.sans24)
            draw.string(t2, 180, y+18, width=46)

            self._last_count = self.count

class ConfirmationView:
    """Confirmation widget allowing user confirmation of a setting."""

    def __init__(self):
        self.active = False
        self.value = False
        self._yes = Button(20, 140, 90, 45, 'Yes')
        self._no = Button(130, 140, 90, 45, 'No')

    def draw(self, message):
        draw = wasp.watch.drawable
        mute = wasp.watch.display.mute

        mute(True)
        draw.set_color(wasp.system.theme('bright'))
        draw.set_font(fonts.sans24)
        draw.fill()
        draw.string(message, 0, 60)
        self._yes.draw()
        self._no.draw()
        mute(False)

        self.active = True

    def touch(self, event):
        if not self.active:
            return False

        if self._yes.touch(event):
            self.active = False
            self.value = True
            return True
        elif self._no.touch(event):
            self.active = False
            self.value = False
            return True

        return False
