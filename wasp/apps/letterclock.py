# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 David Diem
# based on clock.py by Daniel Thompson

import wasp

import icons
import fonts
import fonts.clock as digits
import fonts.noto48 as noto48
import fonts.noto48bu as noto48bu
import fonts.sans24 as sans24
import widgets

DIGITS = (
        digits.clock_0,
        digits.clock_1,
        digits.clock_2,
        digits.clock_3,
        digits.clock_4,
        digits.clock_5,
        digits.clock_6,
        digits.clock_7,
        digits.clock_8,
        digits.clock_9
)

MONTH = 'JanFebMarAprMayJunJulAugSepOctNovDec'

class LetterclockApp(object):
    """Simple digital clock application.

    Shows a time (as HH:MM) together with a battery meter and the date.
    """
    NAME = 'Letterclock'
    ICON = icons.clock

    def __init__(self):
        self.on_screen = ( -1, -1, -1, -1, -1, -1 )
    def battery(self):
        draw = wasp.watch.drawable
        h = wasp.watch.battery.level() / 96 * 240
        c = 0xffe0
        if wasp.watch.battery.charging():
            c = 0xffff
        draw.fill(c, 235, 239, 4, h)

    def draw(self):
        """Redraw the display from scratch."""
        draw = wasp.watch.drawable        
        draw.fill(0)
        self.on_screen = ( -1, -1, -1, -1, -1, -1 )
        self.update()
        
    def foreground(self):
        self.draw()
        wasp.system.request_tick(1000)        
        
    def update(self):
        """Update the display (if needed).

        The updates are a lazy as possible and rely on an prior call to
        draw() to ensure the screen is suitably prepared.
        """
        now = wasp.watch.rtc.get_localtime()
        if now[3] == self.on_screen[3] and now[4] == self.on_screen[4]:
            if now[5] != self.on_screen[5]:
                self.battery()
                self.on_screen = now
            return False

        draw = wasp.watch.drawable
        month = now[1] - 1
        month = MONTH[month*3:(month+1)*3]

        stunda = ["zwölfe", "oas", "zwoa", "drü", "viere", "füfe", "sechse", "simne", "achte", "nüne", "zehne", "oalfe"]
        minuta = ["", "uas", "zwoa", "drü", "vier", "füf", "sechs", "siba", "acht", "nü", "zeha", "oalf", "zwölf", "drize", "virze", "füfze", "seachze", "sibze", "achze", "nünze", "zwuanzg"]

        if now[4] == 0:
            say = ("", "", "", stunda[now[3] % 12])
        elif now[4] == 15:
            say = ("viertl", "noch", "", stunda[now[3] % 12])
        elif now[4] == 30:
            say = ("", "", "halbe", stunda[(now[3]+1) % 12])
        elif 0 < now[4] < 21:
            say = (minuta[now[4]], "noch", "", stunda[now[3] % 12])
        elif 30 < now[4] < 40:
            say = (minuta[now[4]-30], "noch", " halbe ", stunda[(now[3]+1) % 12])
        elif 20 < now[4] < 30:
            say = (minuta[30-now[4]], "vor", " halbe ", stunda[(now[3]+1) % 12])
        elif now[4] == 45:
            say = ("viertl", "vor", "", stunda[(now[3]+1) % 12])
        elif 39 < now[4] < 60:
            say = (minuta[60-now[4]], "vor", "", stunda[(now[3]+1) % 12])
        else:
            say = ("s", "h", "i t", now[4])

        draw.fill(0)
        draw.set_color(0x0000, bg=0xffe0)
        draw.set_font(noto48bu)
        draw.string(say[0], 0, 20)
        draw.string("{}{}".format(say[1],say[2]), 0, 80)
        draw.string(say[3], 0, 140)
        draw.set_color(0xffe0, bg=0x0000)
        draw.set_font(sans24)
        draw.string("{}{}:{}{}".format(now[3] // 10, now[3] % 10,now[4] // 10, now[4] % 10), 0, 200)        
        self.on_screen = now
        self.battery()
        return True
    
    def sleep(self):
        return True

    def wake(self):
        self.update()

    def tick(self, ticks):
        self.update()
