# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 Johannes Wache

import wasp
import icons

MONTH = 'JanFebMarAprMayJunJulAugSepOctNovDec'

class FibonacciClockApp():
    """Displays the time as a Fibonacci Clock
    """
    NAME = 'Fibo'
    ICON = icons.app

    def __init__(self):
        self.meter = wasp.widgets.VerticalBatteryMeter()
        self.fields = [5,3,2,1,1]
        self.field_colors = [0,0,0,0,0]
        self.color_codes = [0xffff,0xf800,0x07e0,0x001f] # White, red, green and blue

    def foreground(self):
        """Activate the application."""
        self.on_screen = ( -1, -1, -1, -1, -1, -1 )
        self.draw()
        wasp.system.request_tick(1000)

    def sleep(self):
        return True

    def wake(self):
        self.update()

    def tick(self, ticks):
        self.update()
    
    def calculateColors(self,hr,mn):
        self.field_colors = [0,0,0,0,0]
        if (hr >= 12):
            hr -= 12
        for i in range(5):
            if ((hr - self.fields[i]) >= 0):
                hr -= self.fields[i]
                self.field_colors[i] += 1
            
            if ((mn - self.fields[i]) >= 0):
                mn -= self.fields[i]
                self.field_colors[i] += 2
        

    def draw(self):
        """Redraw the display from scratch."""
        draw = wasp.watch.drawable

        draw.fill()
        self.on_screen = ( -1, -1, -1, -1, -1, -1 )
        self.update()
        self.meter.draw()

    def update(self):
        """Update the display (if needed).

        The updates are a lazy as possible and rely on an prior call to
        draw() to ensure the screen is suitably prepared.
        """
        now = wasp.watch.rtc.get_localtime()
        if now[3] == self.on_screen[3] and now[4] == self.on_screen[4]:
            if now[5] != self.on_screen[5]:
                self.meter.update()
                self.on_screen = now
            return False
        draw = wasp.watch.drawable

        #calculate colors of fields:
        self.calculateColors(now[3],now[4] // 5) # Clock can only display every 5 minutes

        draw.fill(x=71,y=41,w=23,h=23,bg=self.color_codes[self.field_colors[4]]) # 1 field
        draw.fill(x=71,y=66,w=23,h=23,bg=self.color_codes[self.field_colors[3]]) # 1 field
        draw.fill(x=21,y=41,w=48,h=48,bg=self.color_codes[self.field_colors[2]]) # 2 field
        draw.fill(x=21,y=91,w=73,h=73,bg=self.color_codes[self.field_colors[1]]) # 3 field
        draw.fill(x=96,y=41,w=123,h=123,bg=self.color_codes[self.field_colors[0]]) # 5 field

        self.on_screen = now

        month = now[1] - 1
        month = MONTH[month*3:(month+1)*3]
        draw.string('{}. {} {}'.format(now[2], month, now[0]),
                0, 185, width=240)

        self.meter.update()
        return True
