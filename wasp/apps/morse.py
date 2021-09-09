# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2021 Francesco Gazzetta

"""Morse translator and notepad
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This app is a simple morse translator that also doubles as a notepad.
Swipe up for a line, swipe down for a dot, tap for end letter, double tap for
end word.
Up to 7 lines of translation will be displayed on a 240x240 screen, and old
lines will be deleted.
There is a preview of the next letter at the bottom of the screen.


.. figure:: res/MorseApp.png
    :width: 179
"""

import wasp
import icons
import fonts
from math import floor
from micropython import const


_WIDTH = const(240)
_HEIGHT = const(240)
# No easy way to make this depend on _WIDTH
_MAXINPUT = const(16)

# These two need to match
_FONTH = const(24)
_FONT = fonts.sans24

_LINEH = int(_FONTH * 1.25)
_MAXLINES = floor(_HEIGHT / _LINEH) - 1 # the "-1" is the input line

_code = {
        ""     : " ",

        ".-"   : "A",
        "-..." : "B",
        "-.-." : "C",
        "-.."  : "D",
        "."    : "E",
        "..-." : "F",
        "--."  : "G",
        "...." : "H",
        ".."   : "I",
        ".---" : "J",
        "-.-"  : "K",
        ".-.." : "L",
        "--"   : "M",
        "-."   : "N",
        "---"  : "O",
        ".--." : "P",
        "--.-" : "Q",
        ".-."  : "R",
        "..."  : "S",
        "-"    : "T",
        "..-"  : "U",
        "...-" : "V",
        ".--"  : "W",
        "-..-" : "X",
        "-.--" : "Y",
        "--.." : "Z",

        ".----": "1",
        "..---": "2",
        "...--": "3",
        "....-": "4",
        ".....": "5",
        "-....": "6",
        "--...": "7",
        "---..": "8",
        "----.": "9",
        "-----": "0",
        }

class MorseApp():
    NAME = 'Morse'
    # 2-bit RLE, 96x64, generated from res/morse_icon.png, 143 bytes
    ICON = (
        b'\x02'
        b'`@'
        b'?\xff\xff\xff\xff\x13\xc4?\x1c\xc6?\x1b\xc6?\x1b\xc6'
        b'?\x1a\xc8?\x19\xc8?\x18\xca?\x17\xc4\x02\xc4?\x17'
        b'\xc4\x02\xc4?\x16\xc5\x02\xc5?\x15\xc4\x04\xc4?\x15\xc4'
        b'\x04\xc4?\x14\xc4\x06\xc4?\x13\xc4\x06\xc4?\x12\xc5\x06'
        b'\xc5?\x11\xc4\x08\xc4?\x11\xd0?\x10\xd2?\x0f\xd2?'
        b'\x0e\xc5\n\xc4?\x0e\xc4\x0c\xc4?\r\xc4\x0c\xc4?\x0c'
        b'\xc5\x0c\xc5?\x0b\xc4\x0e\xc4?\x0b\xc4\x0e\xc4?\n\xc4'
        b'\x10\xc4?\xff\xff\xff\xff\x83\xc4\x0e\xda4\xc4\x0e\xda4'
        b'\xc4\x0e\xda4\xc4\x0e\xda?\xff\xff\xff\xfe'
    )

    def __init__(self):
        self.letter = ""
        self.text = [""]
        pass

    def foreground(self):
        self._draw()
        wasp.system.request_event(wasp.EventMask.TOUCH |
                                  wasp.EventMask.SWIPE_UPDOWN)

    def swipe(self, event):
        if len(self.letter) < _MAXINPUT:
            self.letter += "-" if event[0] == wasp.EventType.UP else "."
            self._update()

    def touch(self, event):
        addition = _code[self.letter] if self.letter in _code else "/{}/".format(self.letter)
        self.letter = ""
        merged = self.text[-1] + addition
        # Check if the new text overflows the screen and add a new line if that's the case
        split = wasp.watch.drawable.wrap(merged, _WIDTH)
        if len(split) > 2:
            self.text.append(self.text[-1][split[1]:split[2]] + addition)
            self.text[-2] = self.text[-2][split[0]:split[1]]
            if len(self.text) > _MAXLINES:
                self.text.pop(0)
            # Ideally a full refresh should be done only when we exceed
            # _MAXLINES, but this should be fast enough
            self._draw()
        else:
            self.text[-1] = merged
        self._update()

    def _draw(self):
        """Draw the display from scratch"""
        draw = wasp.watch.drawable
        draw.fill()
        i = 0
        for line in self.text:
            draw.string(line, 0, _LINEH * i)
            i += 1
        self._update()

    def _update(self):
        """Update the dynamic parts of the application display, specifically the
        input line and last line of the text.
        The full text area is updated in _draw() instead."""
        draw = wasp.watch.drawable
        draw.string(self.text[-1], 0, _LINEH*(len(self.text)-1))
        guess = _code[self.letter] if self.letter in _code else "?"
        draw.string("{} {}".format(self.letter, guess), 0, _HEIGHT - _FONTH, width=_WIDTH)

