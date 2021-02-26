# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 Daniel Thompson

import wasp
import array
import random
from micropython import const
import fonts

_COL_X = const(0b11111_000000_00000)
_COL_Y = const(0b00000_111111_00000)
_COL_Z = const(0b00000_000000_11111)

_GREY = const(0x7BEF)
_DARK_GREY = const(0x3186)

_GRAPH_HEIGHT = const(50)
_HALF_GRAPH_HEIGHT = const(_GRAPH_HEIGHT//2)

_POS_X = const(64+8)
_POS_Y = const(64+8+58)
_POS_Z = const(64+8+58+58)

class AccelerationApp():
    """A continously updating graph of accelerometer values
    """
    NAME = 'Accel'

    def foreground(self):
        draw = wasp.watch.drawable
        draw.fill()

        wasp.system.bar.clock = True
        wasp.system.bar.draw()

        draw.set_color(wasp.system.theme('bright'))
        draw.set_font(fonts.sans24)
        draw.string('Accelerometer', 0, 38, width=240)

        # graph areas
        draw.fill(_DARK_GREY, 0, _POS_X, 240, _GRAPH_HEIGHT)
        draw.fill(_DARK_GREY, 0, _POS_Y, 240, _GRAPH_HEIGHT)
        draw.fill(_DARK_GREY, 0, _POS_Z, 240, _GRAPH_HEIGHT)

        # zero lines
        draw.fill(_GREY, 0, _POS_X+_HALF_GRAPH_HEIGHT, 240, 1)
        draw.fill(_GREY, 0, _POS_Y+_HALF_GRAPH_HEIGHT, 240, 1)
        draw.fill(_GREY, 0, _POS_Z+_HALF_GRAPH_HEIGHT, 240, 1)

        if 'acceleration' not in dir(wasp.watch.accel):
            # no support from accelerometer driver
            draw.string('Unsupported', 0, 120-16, width=240)
            draw.string('Device', 0, 120+16, width=240)
            return

        # setup buffers. We keep them to undraw old values, we could also do full redraws from buffer
        self._x = bytearray(240)
        self._y = bytearray(240)
        self._z = bytearray(240)
        self._pos = 0

        wasp.system.request_tick(1000 // 8)


    def background(self):
        if('_x' in dir(self)):
            del self._x
            del self._y
            del self._z

    def tick(self, ticks):
        """Notify the application that its periodic tick is due."""

        wasp.system.keep_awake()

        draw = wasp.watch.drawable

        wasp.system.bar.update()

        # to test on unsupported devices you can use this instead of wasp.watch.accel.acceleration 
        #(x, y, z) = (random.uniform(-2*9.81, 2*9.81), random.uniform(-2*9.81, 2*9.81), random.uniform(-2*9.81, 2*9.81))

        (x, y, z) = wasp.watch.accel.acceleration

        x = -int((x/(2*9.81)+1)*_HALF_GRAPH_HEIGHT)+_POS_X+_GRAPH_HEIGHT
        y = -int((y/(2*9.81)+1)*_HALF_GRAPH_HEIGHT)+_POS_Y+_GRAPH_HEIGHT
        z = -int((z/(2*9.81)+1)*_HALF_GRAPH_HEIGHT)+_POS_Z+_GRAPH_HEIGHT

        pos = self._pos
        nex = (pos+1)%240

        # erase one old datapoint and draw current one
        # erase one data point ahead on the graph to make transition point a bit more obvious

        #x
        draw.fill(_DARK_GREY, nex, self._x[nex], 1, 1)
        draw.fill(_GREY, nex, _POS_X+_HALF_GRAPH_HEIGHT, 1, 1)
        draw.fill(_COL_X, pos, x, 1, 1)

        #y
        draw.fill(_DARK_GREY, nex, self._y[nex], 1, 1)
        draw.fill(_GREY, nex, _POS_Y+_HALF_GRAPH_HEIGHT, 1, 1)
        draw.fill(_COL_Y, pos, y, 1, 1)

        #z
        draw.fill(_DARK_GREY, nex, self._z[nex], 1, 1)
        draw.fill(_GREY, nex, _POS_Z+_HALF_GRAPH_HEIGHT, 1, 1)
        draw.fill(_COL_Z, pos, z, 1, 1)

        self._x[pos] = x
        self._y[pos] = y
        self._z[pos] = z

        self._pos = nex
