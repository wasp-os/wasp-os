'''CPR Assist
~~~~~~~~~~~~~~~~
Tool which alternates between chest compressions and rescue breaths endlessly.

Reimplementation of: https://github.com/espruino/BangleApps/tree/master/apps/cprassist
'''

import wasp
import os
import fonts

COMPRESSION_COUNT = 30
BREATH_COUNT = 2
COMPRESSION_RPM = 100
BREATH_PERIOD_SEC = 4
COLORS = [wasp.system.theme('bright'), wasp.system.theme('mid')]
class CprApp():
    """Provides assistance while performing a CPR"""
    NAME = "CPR"

    def __init__(self):
        self.counter = 0

    def foreground(self):
        wasp.system.request_tick(60000/COMPRESSION_RPM)
        self._draw()

    def tick(self, ticks):
        wasp.system.keep_awake()
        self.provideFeedback()
        if self.counter == 1:
            wasp.system.request_tick(1000 * BREATH_PERIOD_SEC)
            self._draw()  
            self.counter -= 1
            return      
        else:
            wasp.system.request_tick(60000/COMPRESSION_RPM)
            

        if self.counter == 0:
            self.counter = COMPRESSION_COUNT
            self.counter -= 1
            self._draw()
            return
        
        
        self.counter -= 1
        self.update()


    def provideFeedback(self):
        if self.counter > 0:
            wasp.watch.vibrator.pulse()
        else:
            wasp.watch.vibrator.pulse(50, 80)

    def update(self):
        draw = wasp.watch.drawable
        if self.counter > 0:
            draw.set_font(fonts.sans36)
            draw.set_color(COLORS[self.counter % 2])
            draw.string(str(self.counter), 0, 100, width=240)
        else:
            draw.set_color(wasp.system.theme('bright'))
            draw.string("RESCUE", 0, 70, width=240)
            draw.string("BREATHS", 0, 120, width=240)

        draw.set_color(wasp.system.theme('mid'))
        draw.set_font(fonts.sans24)
        draw.string(str(COMPRESSION_COUNT) + ' / ' + str(BREATH_COUNT), 0, 200, width=240)

    def _draw(self):
        draw = wasp.watch.drawable
        draw.reset()
        draw.fill()

        self.update()