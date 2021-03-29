# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 Daniel Thompson
# Copyright (C) 2020 Carlos Gil

"""Phone for GadgetBridge and wasp-os companion
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    .. figure:: res/PhoneApp.png
        :width: 179

        Screenshot of the Phone application

Phone Controller:

* Touch: answer/end
* Event BACK: ignore/close

"""

import wasp

import icons
import time

from micropython import const

DISPLAY_WIDTH = const(240)
ICON_SIZE = const(72)
CENTER_AT = const((DISPLAY_WIDTH - ICON_SIZE) // 2)

class PhoneApp(object):
    """ Phone application."""
    NAME = 'Phone'

    def __init__(self):
        self._anwser = wasp.widgets.GfxButton(24, CENTER_AT, icons.phone)
        self._end = wasp.widgets.GfxButton(DISPLAY_WIDTH - ICON_SIZE - 24, CENTER_AT, icons.hangup)
        self._state = "end"
        self._name = ''
        self._number = ''
        self._state_changed = True
        self._name_changed = True
        self._number_changed = True

    def _send_cmd(self, cmd):
        print('\r')
        for i in range(1):
            for i in range(0, len(cmd), 20):
                print(cmd[i: i + 20], end='')
                time.sleep(0.2)
            print(' ')
        print(' ')

    def _fill_space(self, key):
        if key == 'top':
            wasp.watch.drawable.fill(
                x=0, y=0, w=DISPLAY_WIDTH, h=CENTER_AT)
        elif key == 'down':
            wasp.watch.drawable.fill(x=0, y=CENTER_AT + ICON_SIZE,
                                     w=DISPLAY_WIDTH,
                            h=DISPLAY_WIDTH - (CENTER_AT + ICON_SIZE))

    def foreground(self):
        """Activate the application."""
        number = wasp.system.phonestate.get('number')
        name = wasp.system.phonestate.get('name')
        state = wasp.system.phonestate.get('cmd')

        if number:
            self._number = number
        if name:
            self._name = name
        if state:
            self._state = state
        wasp.watch.drawable.fill()
        self.draw()
        wasp.system.request_tick(1000)
        wasp.system.request_event(wasp.EventMask.TOUCH)

    def background(self):
        """De-activate the application (without losing state)."""
        self._state_changed = True
        self._name_changed = True
        self._number_changed = True

    def tick(self, ticks):
        wasp.system.keep_awake()
        state_now = wasp.system.phonestate.get('cmd')
        name_now = wasp.system.phonestate.get('name')
        number_now = wasp.system.phonestate.get('number')
        if state_now:
            if state_now != self._state:
                self._state = state_now
                self._state_changed = True
        else:
            self._state_changed = False
        if name_now:
            if name_now != self._name:
                self._name = name_now
                self._name_changed = True
        else:
            self._name_changed = False
        if number_now:
            if number_now != self._number:
                self._number = number_now
                self._number_changed = True
        else:
            self._number_changed = False
        wasp.system.phonestate = {}
        self._update()

    def touch(self, event):
        if self._anwser.touch(event):
            self._send_cmd('{"t":"call", "n":"ACCEPT"} ')
            wasp.system.navigate(wasp.EventType.BACK)
        elif self._end.touch(event):
            self._send_cmd('{"t":"call", "n":"REJECT"} ')
            wasp.system.navigate(wasp.EventType.BACK)

    def draw(self):
        """Redraw the display from scratch."""
        self._draw()

    def _draw(self):
        """Redraw the updated zones."""
        if self._state_changed:
            self._anwser.draw()
        if self._name_changed:
            self._draw_label(self._name, 24 + 144)
        if self._number_changed:
            self._draw_label(self._number, 12)
        self._end.draw()

    def _draw_label(self, label, pos):
        """Redraw label info"""
        if label:
            draw = wasp.watch.drawable
            chunks = draw.wrap(label, 240)
            self._fill_space(pos)
            for i in range(len(chunks)-1):
                sub = label[chunks[i]:chunks[i+1]].rstrip()
                draw.string(sub, 0, pos + 24 * i, 240)

    def _update(self):
        if(self._state == "start" or self._state == "incoming"):
            wasp.watch.vibrator.pulse(ms=wasp.system.notify_duration)


    def update(self):
        pass