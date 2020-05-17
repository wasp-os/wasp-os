# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 Daniel Thompson

"""Logo demo for PineTime
~~~~~~~~~~~~~~~~~~~~~~~~~

This demo is simply an alternating sweep of the Pine64 and
MicroPython logos. It cycles through a variety of colours
and swaps between the logos every 5 images (so if you change
anything make sure len(colors) is not a multiple of 5).
"""

import wasp
import icons

# 2-bit RLE, generated from res/demo_icon.png, 292 bytes
demo_icon = (
    b'\x02'
    b'`@'
    b'.\xc1?\x1f\xc3?\x1d\xc5?\x1b\xc7?\x19\xc9?\x17'
    b'\xcb?\x16\xcc?\x10\xc1\x06\xc8\x06\xc1?\n\xc4\x06\xc4'
    b'\x06\xc3?\n\xc6\x0c\xc6?\x08\xc9\x08\xc8?\x08\xc7\x0c'
    b'\xc7?\x06\xc6\x06\xc4\x06\xc5?\x06\xc4\x05\xc9\x06\xc3?'
    b'\x06\xc1\x06\xce\x05\xc2?\n\xd2?\x0c\xd7?\x08\xdc?'
    b'\x05\xdc\x05\xc18\xc3\x05\xd7\x06\xc38\xc5\x06\xd2\x05\xc6'
    b'8\xc7\x06\xce\x05\xc88\xca\x05\xc9\x06\xca8\xcc\x06\xc4'
    b'\x06\xcc8\xce\x0b\xcf8\xd0\x08\xd08\xce\x0b\xcf8\xcc'
    b'\x06\xc4\x06\xcc8\xc9\x06\xc9\x06\xca8\xc7\x06\xcd\x06\xc8'
    b'8\xc5\x06\xd2\x06\xc58\xc3\x05\xd7\x06\xc3>\xdb\x06\xc1'
    b'<\xe08\xc2\x06\xdf\x07\xc12\xc3\x06\xdb\x06\xc42\xc6'
    b'\x06\xd6\x06\xc54\xc7\x06\xd1\x06\xc84\xca\x05\xcd\x06\xc9'
    b'6\xcb\x06\xc8\x05\xcc6\xcd\x06\xc3\x06\xcd7\xd0\n\xcf'
    b'8\xd0\x08\xd08\xce\x05\xc1\x06\xcd:\xca\x06\xc5\x06\xcb'
    b':\xc8\x06\xca\x05\xc8<\xc5\x05\xcf\x06\xc5<\xc3\x05\xd3'
    b'\x06\xc2?\x04\xd8?\x07\xdc?\x05\xdb?\x08\xd7?\r'
    b'\xd2?\x11\xce?\x15\xc9?\x1a\xc5?\x1d\xc3?\x1e\xc3'
    b'?\x1e\xc3?\x1e\xc3?\x1e\xc3?\x1e\xc3?\x1e\xc3?'
    b'Q'
)

colors = (
        0xffff,
        0xf800, # red
        0xffff,
        0xffe0, # yellow
        0xffff,
        0x07e0, # green
        0xffff,
        0x07ff, # cyan
        0xffff,
        0x001f, # blue
        0xffff,
        0xf81f, # magenta
    )

class Hack:
    """wasptool uses class (starting in column 0) as a clue for chunk at a
    time transmission. Hence we use fake classes to demark places it is safe
    to split an evaluation.
    """
    pass

# 1-bit RLE, generated from res/pine64.png, 961 bytes
pine64 = (
    240, 240,
    b'x\x01\xee\x03\xec\x05\xea\x07\xe8\t\xe6\x0b\xe4\r\xe2\x0f'
    b'\xe0\x11\xde\x13\xdc\x15\xda\x17\xd8\x19\xd6\x1b\xd4\x1d\xd2\x1f'
    b"\xd1 \xcf!\xce#\xcc%\xca'\xc8)\xc6+\xc4-"
    b"\xc3-\xc6'\xcb#\xd0\x1d\xb6\x02\x1d\x19\x1b\x03\x99\x05"
    b'\x1e\x13\x1c\x05\x99\x08\x1d\x0f\x1c\x08\x98\n\x1e\t\x1d\n'
    b'\x97\r\x1e\x05\x1c\r\x97\x10:\x10\x96\x126\x12\x95\x15'
    b'1\x15\x95\x17-\x18\x93\x1b(\x1a\x93\x1d$\x1c\x93\x1e'
    b'!\x1f\x91\x1d%\x1d\x91\x1b*\x1a\x91\x19.\x19\x8f\x17'
    b'\x19\x01\x19\x17\x8f\x15\x19\x05\x19\x15\x8f\x13\x19\t\x1a\x13'
    b'\x8d\x12\x19\r\x1a\x11\x8d\x10\x18\x12\x1a\x10\x8c\r\x19\x17'
    b'\x19\x0e\x8b\x0c\x19\x1b\x19\x0c\x8b\n\x19\x1f\x1a\n\x89\t'
    b'\x18$\x1a\x08\x89\x07\x18)\x19\x06\x89\x04\x19-\x19\x05'
    b'\x87\x03\x191\x19\x03\x87\x01\x186\x19\x01\x9e;\xb3?'
    b'\xafC\xabG\xa6L\xa2Q\x9dU\x98Z\x94^\x90c'
    b'\x8bg\x87k\x85kn\x01\x18f\x1a\x01V\x03\x19a'
    b'\x1a\x03V\x05\x19]\x1a\x05V\x07\x19Y\x19\x08V\n'
    b'\x18T\x1a\nV\x0c\x19O\x1a\x0cV\x0e\x19K\x19\x0f'
    b'V\x11\x18G\x19\x11V\x13\x18B\x1a\x13V\x16\x18='
    b'\x19\x16V\x18\x189\x19\x18V\x1a\x185\x19\x1aV\x1c'
    b"\x181\x19\x1cV\x1f\x18+\x19\x1fV!\x18'\x19!"
    b'V#\x18#\x19#V%\x18\x1f\x18&V(\x17\x1a'
    b'\x19(V*\x18\x15\x19*V,\x18\x11\x18-V/'
    b'\x17\r\x18/V1\x17\x08\x191V4\x17\x03\x184'
    b'V6.6V8*8V:&:V= ='
    b'V<"<V:&:V7+8V505'
    b'V3\x19\x01\x1a3V0\x1a\x05\x1b0V.\x19\x0b'
    b"\x1a.V,\x19\x0f\x1a,V)\x1a\x13\x1b)V'"
    b"\x1a\x17\x1b'V%\x19\x1d\x1a%V#\x19!\x1a#"
    b'V \x1a%\x1b V\x1e\x1a)\x1b\x1eV\x1c\x1a.'
    b'\x1a\x1cV\x19\x1b2\x1b\x19V\x17\x1a7\x1b\x17V\x14'
    b'\x1b<\x1a\x15V\x12\x1b@\x1b\x12V\x10\x1aE\x1b\x10'
    b'V\x0e\x1aI\x1b\x0eV\x0b\x1bM\x1c\x0bV\t\x1bQ'
    b'\x1c\tV\x07\x1aW\x1b\x07V\x04\x1b[\x1b\x05V\x02'
    b'\x1b_\x1c\x02qc\x8ai\x85m\x81q}uyz'
    b'vyZ\x03\x1cu\x1d\x03=\x04\x1cq\x1d\x04>\x06'
    b'\x1cm\x1d\x06?\x08\x1ch\x1c\x08@\n\x1cd\x1c\n'
    b'A\x0c\x1b_\x1c\x0cB\x0e\x1b[\x1c\x0eB\x11\x1bV'
    b'\x1b\x11C\x12\x1bR\x1b\x12D\x14\x1bM\x1c\x14E\x16'
    b'\x1aI\x1b\x16F\x18\x1aE\x1b\x18G\x1a\x1a?\x1b\x1a'
    b'H\x1c\x1a;\x1b\x1cI\x1e\x197\x1a\x1eJ \x193'
    b'\x1a J"\x1a-\x1b!L$\x19)\x1a$L&'
    b"\x19%\x1a&M(\x18!\x1a'N*\x19\x1c\x19*"
    b'O+\x19\x18\x19+P.\x18\x13\x19.Q/\x18\x0f'
    b'\x19/R2\x18\n\x182S3\x18\x05\x193T5'
    b'\x18\x01\x195T8,8U9(9V<"<'
    b'W< <X:$:Y7(7Z4-5'
    b'Z222[/\x1a\x01\x1b/\\-\x19\x06\x1b-'
    b"])\x1a\x0b\x1b)^'\x1a\x0f\x1b'_$\x1a\x13"
    b'\x1b$`!\x1a\x19\x1b!a\x1e\x1a\x1d\x1b\x1eb\x1c'
    b'\x1a!\x1b\x1cc\x19\x1a%\x1b\x19d\x16\x1a*\x1c\x16'
    b'd\x14\x1a/\x1b\x14e\x11\x1a3\x1b\x11f\x0f\x1a7'
    b'\x1b\x0fg\x0b\x1a<\x1c\x0bh\t\x1a@\x1c\ti\x06'
    b'\x1aE\x1b\x06j\x03\x1bI\x1c\x03\x86M\xa0S\x9bW'
    b'\x97[\x93_\x8ee\x89i\x85m\x85i\x89e\x8d`'
    b'\x93[\x97W\x9bS\x9fN\xa5I\xa9E\xadA\xb1<'
    b'\xb68\xbb3\xbf/\xc3+\xc7&\xcd!\xd1\x1d\xd5\x19'
    b'\xda\x13\xdf\x0f\xe2\x0c\xe4\x0c\xe4\x0c\xe4\x0c\xe4\x0c\xe4\x0c'
    b'\xe4\x0c\xe4\x0c\xe4\x0c\xe4\x0c\xe4\x0c\xe4\x0c\xe4\x0c\xe4\x0c'
    b'\xe4\x0c\xe4\x0c\xe4\x0c\xe4\x0c\xe4\x0c\xe4\x0c\xe4\x0c\xe4\x0c'
    b'\xe4\x0c\xe4\x0c\xe4\x0c\xe4\x0c\xe4\x0c\xe4\x0c\xe4\x0c\xe4\x0c'
    b's'
)

class Hack:
    pass

# 1-bit RLE, generated from res/micropython.png, 1491 bytes
micropython = (
    240, 240,
    b'\xff\x00\xff\x00\xff\x00\xff\x00\xff\x00\xff\x00\xff\x00\xff\x00'
    b'\xff\x00\xff\x00\xff\x00\xff\x00\xff\x00\xff\x00\xff\x00\x1fc'
    b'\tc!c\tc!c\tc!c\tc!c'
    b'\tc!c\tc!c\tc!c\tc!c'
    b'\tc!c\tc!c\tc!c\tc!c'
    b'\tc!c\tc!c\tc!c\tc!c'
    b'\tc!c\tc!c\tc!c\tc!c'
    b'\tc!c\tc!c\tc!c\tc!c'
    b'\tc!c\tc!c\tc!c\tc!c'
    b'\tc!c\tc!c\tc!c\tc!c'
    b'\tc!c\tc!c\tc!c\tc!c'
    b'\tc!c\tc!c\tc!c\tc!c'
    b'\tc!c\tc!c\tc!c\tc!c'
    b'\tc!-\t-\t-\t-!-\t-\t-'
    b'\t-!-\t-\t-\t-!-\t-\t-'
    b'\t-!-\t-\t-\t-!-\t-\t-'
    b'\t-!-\t-\t-\t-!-\t-\t-'
    b'\t-!-\t-\t-\t-!-\t-\t-'
    b'\t-!-\t-\t-\t-!-\t-\t-'
    b'\t-!-\t-\t-\t-!-\t-\t-'
    b'\t-!-\t-\t-\t-!-\t-\t-'
    b'\t-!-\t-\t-\t-!-\t-\t-'
    b'\t-!-\t-\t-\t-!-\t-\t-'
    b'\t-!-\t-\t-\t-!-\t-\t-'
    b'\t-!-\t-\t-\t-!-\t-\t-'
    b'\t-!-\t-\t-\t-!-\t-\t-'
    b'\t-!-\t-\t-\t-!-\t-\t-'
    b'\t-!-\t-\t-\t-!-\t-\t-'
    b'\t-!-\t-\t-\t-!-\t-\t-'
    b'\t-!-\t-\t-\t-!-\t-\t-'
    b'\t-!-\t-\t-\t-!-\t-\t-'
    b'\t-!-\t-\t-\t-!-\t-\t-'
    b'\t-!-\t-\t-\t-!-\t-\t-'
    b'\t-!-\t-\t-\t-!-\t-\t-'
    b'\t-!-\t-\t-\t-!-\t-\t-'
    b'\t-!-\t-\t-\t-!-\t-\t-'
    b'\t-!-\t-\t-\t-!-\t-\t-'
    b'\t-!-\t-\t-\t-!-\t-\t-'
    b'\t-!-\t-\t-\t-!-\t-\t-'
    b'\t-!-\t-\t-\t-!-\t-\t-'
    b'\t-!-\t-\t-\t-!-\t-\t-'
    b'\t-!-\t-\t-\t-!-\t-\t-'
    b'\t-!-\t-\t-\t-!-\t-\t-'
    b'\t-!-\t-\t-\t-!-\t-\t-'
    b'\t-!-\t-\t-\t-!-\t-\t-'
    b'\t-!-\t-\t-\t-!-\t-\t-'
    b'\t-!-\t-\t-\t-!-\t-\t-'
    b'\t-!-\t-\t-\t-!-\t-\t-'
    b'\t-!-\t-\t-\t-!-\t-\t-'
    b'\t-!-\t-\t-\t-!-\t-\t-'
    b'\t-!-\t-\t-\t-!-\t-\t-'
    b'\t-!-\t-\t-\t-!-\t-\t-'
    b'\t-!-\t-\t-\t-!-\t-\t-'
    b'\t-!-\t-\t-\t-!-\t-\t-'
    b'\t-!-\t-\t-\t-!-\t-\t-'
    b'\t-!-\t-\t-\t-!-\t-\t-'
    b'\t-!-\t-\t-\t-!-\t-\t-'
    b'\t-!-\t-\t-\t-!-\t-\t-'
    b'\t-!-\t-\t-\t-!-\t-\t-'
    b'\t-!-\t-\t-\t-!-\t-\t-'
    b'\t-!-\t-\t-\t-!-\t-\t-'
    b'\t-!-\t-\t-\t-!-\t-\t-'
    b'\t-!-\t-\t-\t-!-\t-\t-'
    b'\t-!-\t-\t-\t-!-\t-\t-'
    b'\t-!-\t-\t-\t-!-\t-\t-'
    b'\t-!-\t-\t-\t-!-\t-\t-'
    b'\t-!-\t-\t-\t-!-\t-\t-'
    b'\t-!-\t-\t-\t-!-\t-\t-'
    b'\t-!-\t-\t-\t-!-\t-\t-'
    b'\t-!-\t-\t-\t-!-\t-\t-'
    b'\t-!-\t-\t-\t-!-\t-\t-'
    b'\t-!-\t-\t-\t-!-\tc\t-'
    b'!-\tc\t-!-\tc\t-!-\tc'
    b'\t-!-\tc\t-!-\tc\t-!-'
    b'\tc\t\x12\x0c\x0f!-\tc\t\x12\x0c\x0f!-'
    b'\tc\t\x12\x0c\x0f!-\tc\t\x12\x0c\x0f!-'
    b'\tc\t\x12\x0c\x0f!-\tc\t\x12\x0c\x0f!-'
    b'\tc\t\x12\x0c\x0f!-\tc\t\x12\x0c\x0f!-'
    b'\tc\t\x12\x0c\x0f!-\tc\t\x12\x0c\x0f!-'
    b'\tc\t\x12\x0c\x0f!-\tc\t\x12\x0c\x0f!-'
    b'\tc\t\x12\x0c\x0f!-\tc\t\x12\x0c\x0f!-'
    b'\tc\t\x12\x0c\x0f!-\tc\t\x12\x0c\x0f!-'
    b'\tc\t\x12\x0c\x0f!-\tc\t\x12\x0c\x0f!-'
    b'\tc\t\x12\x0c\x0f!-\tc\t\x12\x0c\x0f!-'
    b'\tc\t\x12\x0c\x0f!-\tc\t-!-\tc'
    b'\t-!-\tc\t-!-\tc\t-!-'
    b'\tc\t-!-\tc\t-!-\tc\t-'
    b'!-\tc\t-!-\tc\t-!-\tc'
    b'\t-!-\tc\t-!-\tc\t-!-'
    b'\tc\t-!-\tc\t-!-\tc\t-'
    b'!-\tc\t-!-\tc\t-!-\tc'
    b'\t-\xff\x00\xff\x00\xff\x00\xff\x00\xff\x00\xff\x00\xff\x00'
    b'\xff\x00\xff\x00\xff\x00\xff\x00\xff\x00\xff\x00\xff\x00\xff\x00'
    b'\xff\x00\x11'
)
class DemoApp():
    """Application for live demos.

    Start this to give the watch something "interesting" to do when talking
    over demos!
    """
    NAME = 'Demo'
    ICON = demo_icon

    def __init__(self):
        self._logo = pine64
        self._color = 0
        self._i = 0

    def foreground(self):
        """Draw the first frame and establish the tick."""
        self._draw()
        wasp.system.request_tick(2000)

    def tick(self, ticks):
        """Handle the tick."""
        self._draw()
        wasp.system.keep_awake()

    def _draw(self):
        """Draw the next frame."""
        draw = wasp.watch.drawable

        if self._i < 5:
            self._i += 1
        else:
            self._i = 0
            if self._logo == pine64:
                self._logo = micropython
            else:
                self._logo = pine64
            draw.fill()
        draw.rleblit(self._logo, fg=colors[self._color])
        self._color += 1
        if self._color >= len(colors):
            self._color = 0
