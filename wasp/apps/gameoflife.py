# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 Daniel Thompson
"""Conway's Game of Life.

On 11 April 2020 John H. Conway who, among many, many other
achievements, devised the rule set for his Game of Life, died of
complications from a COVID-19 infection.

The Game of Life is the first "toy" program I ever recall seeing on a
computer (running in a mid 1980s Apple Macintosh). It sparked something
even if "toy" is perhaps an underwhelming description of the Game of Life.
Either way it occupies a special place in my childhood. For that, this
application is dedicated to Professor Conway.
"""

import array
import machine
import micropython
import wasp

@micropython.viper
def xorshift12(v: int) -> int:
    """12-bit xorshift pseudo random number generator.

    With only 12-bits of state this PRNG is another toy! It appears
    here because it allows us to visit every possible 12-bit value
    (except zero) whilst taking an interesting route. This allows us to
    make the redraw (which is too slow to fully conceal) visually
    engaging.
    """
    v ^= v << 1
    v ^= (v >> 3) & 0x1ff
    v ^= (v << 7)

    return v & 0xfff

@micropython.viper
def get_color(v: int) -> int:
    """Convert a 12-bit number into a reasonably bright RGB565 pixel"""
    rgb = v ^ (v << 4)
    while 0 == (rgb & 0xc710):
        rgb += 0x2104
    return rgb

@micropython.viper
def get_cell(board, stride: int, x: int, y: int) -> bool:
    b = ptr32(board)
    xw = x >> 5
    xb = x & 0x1f
    yw = y * (stride >> 5)

    return bool(b[yw + xw] & (1 << xb))

@micropython.viper
def set_cell(board, stride: int, x: int, y: int, v: bool):
    b = ptr32(board)
    xw = x >> 5
    xb = x & 0x1f
    yw = y * (stride >> 5)
    m = 1 << xb
    c = b[yw + xw]

    # viper doesn't implement bitwise not so we are having
    # to clear bits using xor...
    if v:
        b[yw + xw] = c | m
    elif c & m:
        b[yw + xw] = c ^ m

@micropython.viper
def game_of_life(b, xmax: int, ymax: int, nb):
    """Run a single generation of Conway's Game of Life

    1. Death by isolation: a cell dies if has fewer than two live neighbours.

    2. Death by overcrowding: a cell dies if it has more than three live
       neighbours.

    3. Survival: a living cell continues to survive if it has two or three
       neighbours.

    4. Reproduction: a dead cell comes alive if it has exactly three
       neighbours.

    In the code below we have simplified the above rules to "a cell is
    alive it has three live neighbours or if it was previously alive
    and has two neighbours, otherwise it is dead.".
    """
    board = ptr32(b)
    next_board = ptr32(nb)

    for y in range(1, ymax-1):
        tm = int(get_cell(board, xmax, 0, y-1))
        tr = int(get_cell(board, xmax, 1, y-1))
        cm = int(get_cell(board, xmax, 0, y))
        cr = int(get_cell(board, xmax, 1, y))
        bm = int(get_cell(board, xmax, 0, y+1))
        br = int(get_cell(board, xmax, 1, y+1))

        for x in range(1, xmax-1):
            tl = tm
            tm = tr
            tr = int(get_cell(board, xmax, x+1, y-1))
            cl = cm
            cm = cr
            cr = int(get_cell(board, xmax, x+1, y))
            bl = bm
            bm = br
            br = int(get_cell(board, xmax, x+1, y+1))

            c = tl + tm + tr + cl + cr + bl + bm + br

            set_cell(next_board, xmax, x, y, c == 3 or (cm and c == 2))

# 2-bit RLE, generated from res/gameoflife.png, 404 bytes
# The icon is a carefully selected generation of an "acorn", I wanted
# to avoid using a glider, they are overused to the point of cliche!
icon = (
    b'\x02'
    b'`@'
    b'?\xff\xff\xee@\xf8B\x02B\x02B?\x16L?\x15'
    b'L?\x16B\x02B\x02B?\x1bB?\x1eD?\x1d'
    b'D?\x1eB?\x17\x80\xee\x82\x02\x82\x06\x82\x02\x82?'
    b'\x0e\x88\x04\x88?\r\x88\x04\x88?\x0e\x82\x02\x82\x06B'
    b'\x02\x82?\x03\xc0\x89\xc2\x02\xc2\x02\xc2\x02\xc2\x02\xc2\x02'
    b'\xc2\x02\xc2\x02\xc2\x02\xc2\x02\xc2\x02\xc25\xec4\xec5'
    b'\xc2\x02\xc2\x02\xc2\x02\xc2\x02\xc2\x02\xc2\x02\xc2\x02\xc2\x02'
    b'\xc2\x02\xc2\x02\xc2*B\x02B\x12\xc2\x06B\x06\xc2\x12'
    b'B\x02B\x1dH\x10\xc4\x04D\x04\xc4\x10H\x1cH\x10'
    b'\xc4\x04D\x04\xc4\x10H\x1dB\x02B\x12\xc2\x06B\x06'
    b'\xc2\x12B\x02B\x1eB\x16\xc2\x0e\xc2\x16B\x1dD\x14'
    b'\xc4\x0c\xc4\x14D\x1cD\x14\xc4\x0c\xc4\x14D\x1dB\x16'
    b'\xc2\x0e\xc2\x16B\x1eB>B\x1dD<D\x1cD<'
    b'D\x1dB>B"B\x02B\x06B\x02B\x02B\x0e'
    b'B\x02B\x02B\x06B\x02B%H\x04L\x0cL\x04'
    b'H$H\x04L\x0cL\x04H%B\x02B\x06B\x02'
    b'B\x02B\x0eB\x02B\x02B\x06B\x02B2B\n'
    b'B\x06B\nB=D\x08D\x04D\x08D<D\x08'
    b'D\x04D\x08D=B\nB\x06B\nB>B\x02'
    b'B\x06\x82\x06\x82\x06B\x02B=H\x04\x84\x04\x84\x04'
    b'H<H\x04\x84\x04\x84\x04H=B\x02B\x06\x82\x06'
    b'\x82\x06B\x02B>\x82\x02\x82\x16\x82\x02\x82=\x88\x14'
    b'\x88<\x88\x14\x88=\x82\x02\x82\x16\x82\x02\x82>\x82\x02'
    b'\x82\x02\x82\x0e\x82\x02\x82\x02\x82=\x8c\x0c\x8c<\x8c\x0c'
    b'\x8c=\x82\x02\x82\x02\x82\x0e\x82\x02\x82\x02\x82?\xff\xff'
    b'\xe2'
)

class GameOfLifeApp():
    """Application implementing Conway's Game of Life.
    """
    NAME = 'Life'
    ICON = icon

    def __init__(self):
        """Initialize the application."""
        self._board = array.array('I', [0] * (64*64//32))
        self._next_board = array.array('I', self._board)
        self._color = 1
        self.touch(None)

    def foreground(self):
        """Activate the application."""
        self._draw()
        wasp.system.request_event(wasp.EventMask.TOUCH)
        wasp.system.request_tick(625)

    def tick(self, ticks):
        """Notify the application that its periodic tick is due."""
        wasp.system.keep_awake()

        #t = machine.Timer(id=1, period=8000000)
        #t.start()

        game_of_life(self._board, 64, 64, self._next_board)
        #t1 = t.time()
        self._update()

        #t2 = t.time()
        #t.stop()
        #del t
        #wasp.watch.drawable.string('{:4.2f}s {:4.2f}s'.format(t1 / 1000000,
        #                                                    t2 / 1000000), 6, 210)

    def touch(self, event):
        """Notify the application of a touchscreen touch event."""
        board = self._next_board
        for i in range(len(board)):
            board[i] = 0
        board[62] = 32 << 16
        board[64] = 8 << 16
        board[66] = 103 << 16

        if None != event:
            self._update()

    def _draw(self):
        """Draw the display from scratch."""
        wasp.watch.drawable.fill()
        board = self._board
        for i in range(len(board)):
            board[i] = 0
        self._update()

    def _update(self):
        """Update the dynamic parts of the application display."""
        b = self._board
        nb = self._next_board
        self._board = nb
        self._next_board = b

        display = wasp.watch.display
        lb = display.linebuffer
        alive = memoryview(lb)[0:2*16]
        self._color = xorshift12(self._color)
        rgbhi = get_color(self._color)
        rgblo = rgbhi & 0xff
        rgbhi >>= 8
        for i in range(0, len(alive), 2):
            alive[i] = rgbhi
            alive[i+1] = rgblo
        for i in (0, 3,  12, 15):
            alive[i*2] = 0
            alive[i*2+1] = 0
        dead = memoryview(lb)[2*16:4*16]
        for i in range(len(dead)):
            dead[i] = 0

        def draw_cell(cell, display, px):
            x = ((cell & 0x3f) - 2) * 4
            y = ((cell >> 6) -2) * 4
            if x < 0 or x >= 240 or y < 0 or y >= 240:
                return

            display.set_window(x, y, 4, 4)
            display.write_data(px)

        draw_cell(1, display, alive if b[1//32] & (1 << (1 & 0x1f)) else dead)
        v = xorshift12(1)
        while 1 != v:
            me = b[v//32] & (1 << (v & 0x1f))
            nx = nb[v//32] & (1 << (v & 0x1f))
            if me != nx:
                draw_cell(v, display, alive if nx else dead)
            v = xorshift12(v)
        draw_cell(0, display, alive if b[0//32] & (1 << (0 & 0x1f)) else dead)
