 
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
import icons
import fonts.clock as digits

DIGITS = (
        digits.clock_0, digits.clock_1, digits.clock_2, digits.clock_3,
        digits.clock_4, digits.clock_5, digits.clock_6, digits.clock_7,
        digits.clock_8, digits.clock_9
)

class FlipRollApp():
    """Tap to flip a coin or roll dice!"""
    NAME = 'Flip Roll'
    ICON = icons.dice

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
