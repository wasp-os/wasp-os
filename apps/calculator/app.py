# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 Johannes Wache
"""Calculator
~~~~~~~~~~~~~

This is a simple calculator app that uses the build-in eval() function to
compute the solution.

.. figure:: res/screenshots/CalculatorApp.png
    :width: 179
"""

import wasp, fonts

# 2-bit RLE, generated from res/calc.png, 413 bytes
calc = (
    b'\x02'
    b'`@'
    b'(@\x03P?\x0eV?\x08[?\x04_?\x01b'
    b'<f9h7j5l3n1p/r-t'
    b'+H\xd1D\xd1H*H\xd2B\xd2H)I\xd2B'
    b"\xd2I'J\xd2B\xd2I'J\xc8\xc2\xc8B\xd2J"
    b'%K\xc7\xc1\x02\xc1\xc7B\xd2J%K\xc7\xc1\x02\xc2'
    b'\xc6B\xd2K$K\xc5\xc2\xc1\x02\xc1\xc2\xc5B\xd2K'
    b'#L\xc4\xc1\x08\xc1\xc4B\xc5\x08\xc5L"L\xc4\xc1'
    b'\x08\xc2\xc3B\xc5\x08\xc1\xc1\xc3L"L\xc5\xc2\xc1\x02'
    b'\xc8B\xcf\xc1\xc2L!M\xc6\xc2\x02\xc8B\xd0\xc1\xc1'
    b'M M\xc7\xc1\x02\xc8B\xd1\xc1M M\xc8\xc2\xc8'
    b'B\xd2M M\xc9\xc1\xc8B\xd2M M\xd2B\xd2'
    b'M M\xd2B\xd2M N\xd0D\xd0N \x7f\x01'
    b' \x7f\x01 N\xd0D\xc1\xcfN M\xd2B\xc1\xd1'
    b'M M\xd2B\xd2AL M\xd2B\xd2AL '
    b'M\xd2B\xd2AL M\xc7\xc1\xcaB\xc5\xc8\xc5A'
    b'L M\xc5\xc1\x02\xc2\x02\xc1\xc5B\xc4\xc1\x08\xc1\xc4'
    b'AL!L\xc5\xc1\x06\xc1\xc5B\xc4\xc1\x08\xc1\xc1\xc3'
    b'AK"L\xc6\xc1\x04\xc1\xc6B\xc6\xca\xc2AK"'
    b'L\xc6\xc1\x04\xc1\xc6B\xc7\xca\xc1L#K\xc5\xc1\x06'
    b'\xc1\xc5B\xc4\xc1\x08\xc1\xc4JA$K\xc5\xc1\x02\xc2'
    b'\x02\xc1\xc5B\xc4\xc1\x08\xc1\xc4K%J\xc6\xc2\xc2\xc2'
    b"\xc6B\xc5\xc8\xc5J&J\xd2B\xc6\xccJ'I\xd2"
    b'B\xc7\xcbI(I\xd2B\xc8\xcaI)H\xd2B\xc9'
    b'\xc9H*H\xd1D\xc9\xc8H+t-r/p1'
    b'n3l5j7h9f<b?\x01^?\x05'
    b'XAA?\tV?\x0eP(')

fields = ( '789+('
           '456-)'
           '123*^'
           'C0./=' )

class CalculatorApp():
    NAME = 'Calc'
    ICON = calc

    def __init__(self):
        self.output = ""

    def foreground(self):
        self._draw()
        self._update()
        wasp.system.request_event(wasp.EventMask.TOUCH)

    def touch(self, event):
        if (event[2] < 48):
            if (event[1] > 200): # undo button pressed
                if (self.output != ""):
                    self.output = self.output[:-1]
        else:
            x = event[1] // 47
            y = (event[2] // 48) - 1

            # Error handling for touching at the border
            if x > 4:
                x = 4
            if y > 3:
                y = 3
            button_pressed = fields[x + 5*y]
            if (button_pressed == "C"):
                self.output = ""
            elif (button_pressed == "="):
                try:
                    self.output = str(eval(self.output.replace('^', '**')))[:12]
                except:
                    wasp.watch.vibrator.pulse()
            else:
                self.output +=  button_pressed
        self._update()

    def _draw(self):
        draw = wasp.watch.drawable
        theme = wasp.system.theme
        line = draw.line
        fill = draw.fill

        hi = theme('bright')
        lo = theme('mid')
        mid = draw.lighten(lo, 2)
        bg = draw.darken(theme('ui'), theme('contrast'))
        bg2 = draw.darken(bg, 2)

        # Draw the background
        fill(0, 0, 0, 239, 47)
        fill(0, 236, 239, 3)
        fill(bg, 141, 48, 239-141, 236-48)
        fill(bg2, 0, 48, 141, 236-48)

        # Make grid:
        draw.set_color(lo)
        for i in range(4):
            # horizontal lines
            line(x0=0,y0=(i+1)*47,x1=239,y1=(i+1)*47)
            # vertical lines
            line(x0=(i+1)*47,y0=47,x1=(i+1)*47,y1=235)
        line(x0=0, y0=47, x1=0, y1=236)
        line(x0=239, y0=47, x1=239, y1=236)
        line(x0=0, y0=236, x1=239, y1=236)

        # Draw button labels
        draw.set_color(hi, bg2)
        for x in range(5):
            if x == 3:
                draw.set_color(mid, bg)
            for y in range(4):
                label = fields[x + 5*y]
                if (x == 0):
                    draw.string(label, x*47+14, y*47+60)
                else:
                    draw.string(label, x*47+16, y*47+60)
        draw.set_color(hi)
        draw.string("<", 215, 10)
    
    def _update(self):
        output = self.output if len(self.output) < 12 else self.output[len(self.output)-12:]
        wasp.watch.drawable.string(output, 0, 14, width=200, right=True)
