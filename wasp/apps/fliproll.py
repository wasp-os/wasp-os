 
# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 Daniel Thompson
# Copyright (C) 2021 Evan Rodgers 'setLillie'

"""Digital Coin Flip
~~~~~~~~~~~~~~~~

Shows a dice roll on screen tap

.. figure:: res/dice_icon.png
    :width: 179
"""

import wasp
from random import randint
import fonts.clock as digits

# 2-bit RLE, generated from /home/flame/wasp-os/res/dice.png, 288 bytes
dice = (
    b'\x02'
    b'`@'
    b'?\xff\xff\x8d\xcc?\x12\xd2?\x0c\xd8?\x08\xcb\x04\xcb'
    b'?\x05\xc8\x0e\xc8?\x02\xc7\x12\xc7?\x00\xc6\x16\xc6='
    b'\xc5\x1a\xc5;\xc5\x1c\xc59\xc5\r\xc4\r\xc57\xc5\x0e'
    b'\xc4\x0e\xc56\xc4\x0f\xc4\x0f\xc45\xc4\x0e\xc8\x0e\xc43'
    b'\xc5\x0c\xcc\x0c\xc52\xc4\x0c\xce\x0c\xc42\xc4\x0c\xce\x0c'
    b'\xc41\xc4\x0c\xc7\x02\xc7\x0c\xc40\xc4\x0c\xc6\x05\xc5\x0c'
    b'\xc40\xc3\r\xc6\x05\xc4\x0e\xc3/\xc4\r\xc6\x17\xc4.'
    b'\xc4\r\xc7\x16\xc4.\xc4\r\xc9\x14\xc4.\xc4\x0e\xcb\x11'
    b'\xc4.\xc3\x0f\xcd\x10\xc3.\xc3\x10\xcd\x0f\xc3.\xc3\x11'
    b'\xcd\x0e\xc3.\xc3\x14\xca\x0e\xc3.\xc4\x15\xc9\x0c\xc4.'
    b'\xc4\x17\xc7\x0c\xc4.\xc4\x0e\xc3\x07\xc6\x0c\xc4.\xc4\x0c'
    b'\xc6\x06\xc6\x0c\xc4/\xc3\x0c\xc6\x06\xc6\x0c\xc30\xc4\x0c'
    b'\xc7\x03\xc6\x0c\xc40\xc4\x0c\xd0\x0c\xc41\xc4\x0c\xce\x0c'
    b'\xc42\xc4\r\xcc\r\xc42\xc5\r\xca\r\xc53\xc4\x10'
    b'\xc4\x10\xc45\xc4\x0f\xc4\x0f\xc46\xc5\x0e\xc4\x0e\xc57'
    b'\xc5\r\xc4\r\xc59\xc5\x1c\xc5;\xc5\x1a\xc5=\xc6\x16'
    b'\xc6?\x00\xc7\x12\xc7?\x02\xc8\x0e\xc8?\x05\xcb\x04\xcb'
    b'?\x08\xd8?\x0c\xd2?\x12\xcc?\xff\xff\x8d'
)

DIGITS = (
        digits.clock_0, digits.clock_1, digits.clock_2, digits.clock_3,
        digits.clock_4, digits.clock_5, digits.clock_6, digits.clock_7,
        digits.clock_8, digits.clock_9
)

class FlipRollApp():
    """Tap to flip a coin or roll dice!"""
    NAME = 'Flip Roll'
    ICON = dice

    def foreground(self):
        wasp.system.bar.clock = True
        self.pages = ('Main', 'Dice', 'Coin')
        self.page = self.pages[0]
        wasp.system.request_event(wasp.EventMask.TOUCH |
                                  wasp.EventMask.SWIPE_UPDOWN)
        self._draw(True)

    def swipe(self, event):
        pages = self.pages
        i = pages.index(self.page)

        if event[0] == wasp.EventType.UP:
            i += 1
            if i >= len(pages):
                i = 0
        else:
            i -= 1
            if i < 0:
                i = len(pages) - 1
        self.page = pages[i]
        self._draw(True)

    def touch(self, event):
        self._draw()


    def _draw(self, redraw=False):
        draw = wasp.watch.drawable
        hi =  wasp.system.theme('bright')

        if redraw:
            draw.fill()
        else:
            if not self.touch:
                # Skip the update
                return
        if self.page == 'Coin':
            coinSide = randint(0, 1)

            if coinSide == 0:
                coinSideText = 'Tails'
            else:
                coinSideText = 'Heads'

            draw.set_color(hi)
            draw.string(coinSideText.format(1, 1, 1),
                    0, 150, width=240)
            draw.string('Tap to flip.'.format(1, 1, 1),
                    0, 180, width=240)

        elif self.page == 'Dice':
            ri1 = randint(1, 6)
            ri2 = randint(1, 6)
            draw.blit(DIGITS[ri1], 3*48, 80, fg=hi)
            draw.blit(DIGITS[ri2], 1*48, 80, fg=hi)
            draw.set_color(hi)
            draw.string('Tap to roll.'.format(1, 1, 1),
                        0, 180, width=240)
        else:
            draw.set_color(hi)
            draw.string('Swipe Up for Dice'.format(1, 1, 1),
                0, 170, width=240)
            draw.string('Down for Coins'.format(1, 1, 1),
                0, 200, width=240)
