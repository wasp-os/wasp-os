# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 Miguel Rochefort
"""Play 2048
~~~~~~~~~~~~

A popular sliding block puzzle game in which tiles are combined to make the
number 2048.

    .. figure:: res/screenshots/Play2048App.png
        :width: 179

        Screenshot of the 2048 game application
"""

import wasp
import icons
import widgets
import random
import fonts
from micropython import const

SCREEN_SIZE = const(240)

GRID_PADDING = const(8)
GRID_SIZE = const(4)
CELL_SIZE = const(50)

GRID_BACKGROUND = const(0x942F)
CELL_BACKGROUND = [0x9CB1, 0xEF3B, 0xEF19, 0xF58F, 0xF4AC, 0xF3EB, 0xF2E7, 0xEE6E, 0xEE6C, 0xEE4A, 0xEE27, 0xEE05]
CELL_FOREGROUND = [0x9CB1, 0x736C, 0x736C, 0xFFBE, 0xFFBE, 0xFFBE, 0xFFBE, 0xFFBE, 0xFFBE, 0xFFBE, 0xFFBE, 0xFFBE]
CELL_LABEL = ['','2','4','8','16','32','64','128','256','512','1K','2K'] # TODO: Display 1024 and 2048 (text-wrapping)

# 2-bit RLE, generated from res/2048_icon.png, 578 bytes
icon = (
    b'\x02'
    b'`@'
    b'\x10\xbf\x01 \xbf\x01 \xbf\x01 \x83@\x81M\x82M'
    b'\x82M\x82\x80\xc8\x8d\xc0\xdb\xc3 \xc3M\xc2M\xc2M'
    b'\xc2\x8d\xc3 \xc3M\xc2M\xc2M\xc2\x8d\xc3 \xc3M'
    b'\xc2M\xc2M\xc2\x8d\xc3 \xc3M\xc2M\xc2M\xc2\x8d'
    b'\xc3 \xc3M\xc2M\xc2M\xc2\x8d\xc3 \xc3M\xc2M'
    b'\xc2M\xc2\x8d\xc3 \xc3M\xc2M\xc2M\xc2\x8d\xc3 '
    b'\xc3M\xc2M\xc2M\xc2\x8d\xc3 \xc3M\xc2M\xc2M'
    b'\xc2\x8d\xc3 \xc3M\xc2M\xc2M\xc2\x8d\xc3 \xc3M'
    b'\xc2M\xc2M\xc2\x8d\xc3 \xc3M\xc2M\xc2M\xc2\x8d'
    b'\xc3 \xff\x01 \xff\x01 \xc3M\xc2M\xc2M\xc2@'
    b'\xfaM\xc3 \xc3\x80\x81\x8d\xc2\x8d\xc2\x8d\xc2M\xc3 '
    b'\xc3\x8d\xc2\x8d\xc2\x8d\xc2M\xc3 \xc3\x8d\xc2\x8d\xc2\x8d'
    b'\xc2M\xc3 \xc3\x8d\xc2\x8d\xc2\x8d\xc2M\xc3 \xc3\x8d'
    b'\xc2\x8d\xc2\x8d\xc2M\xc3 \xc3\x8d\xc2\x8d\xc2\x8d\xc2M'
    b'\xc3 \xc3\x8d\xc2\x8d\xc2\x8d\xc2M\xc3 \xc3\x8d\xc2\x8d'
    b'\xc2\x8d\xc2M\xc3 \xc3\x8d\xc2\x8d\xc2\x8d\xc2M\xc3 '
    b'\xc3\x8d\xc2\x8d\xc2\x8d\xc2M\xc3 \xc3\x8d\xc2\x8d\xc2\x8d'
    b'\xc2M\xc3 \xc3\x8d\xc2\x8d\xc2\x8d\xc2M\xc3 \xff\x01'
    b' \xff\x01 \xc3\xc0\xfb\xcd@\xdbB\x8dB\x8dB\xcd'
    b'C C\xcdB\x8dB\x8dB\xcdC C\xcdB\x8d'
    b'B\x8dB\xcdC C\xcdB\x8dB\x8dB\xcdC '
    b'C\xcdB\x8dB\x8dB\xcdC C\xcdB\x8dB\x8d'
    b'B\xcdC C\xcdB\x8dB\x8dB\xcdC C\xcd'
    b'B\x8dB\x8dB\xcdC C\xcdB\x8dB\x8dB\xcd'
    b'C C\xcdB\x8dB\x8dB\xcdC C\xcdB\x8d'
    b'B\x8dB\xcdC C\xcdB\x8dB\x8dB\xcdC '
    b'C\xcdB\x8dB\x8dB\xcdC \x7f\x01 \x7f\x01 '
    b'C\x8dB\x8dB\x80\xf6\x8dB\x8dC C\xc0\x81\xcd'
    b'B\xcdB\x8dB\x8dC C\xcdB\xcdB\x8dB\x8d'
    b'C C\xcdB\xcdB\x8dB\x8dC C\xcdB\xcd'
    b'B\x8dB\x8dC C\xcdB\xcdB\x8dB\x8dC '
    b'C\xcdB\xcdB\x8dB\x8dC C\xcdB\xcdB\x8d'
    b'B\x8dC C\xcdB\xcdB\x8dB\x8dC C\xcd'
    b'B\xcdB\x8dB\x8dC C\xcdB\xcdB\x8dB\x8d'
    b'C C\xcdB\xcdB\x8dB\x8dC C\xcdB\xcd'
    b'B\x8dB\x8dC \x7f\x01 \x7f\x01 \x7f\x01\x10'
)

class Play2048App():
    """Let's play the 2048 game."""
    NAME = '2048'
    ICON = icon

    def __init__(self):
        """Initialize the application."""
        self._board = None
        self._state = 0
        self._confirmation_view = None

    def foreground(self):
        """Activate the application."""
        wasp.system.request_event(wasp.EventMask.TOUCH |
                                  wasp.EventMask.SWIPE_UPDOWN |
                                  wasp.EventMask.SWIPE_LEFTRIGHT)

        self._state = 0

        if not self._board:
            self._start_game()

        self._draw()

    def touch(self,event):
        """Notify the application of a touchscreen touch event."""
        if self._state == 0:
            if not self._confirmation_view:
                self._confirmation_view = widgets.ConfirmationView()
            self._confirmation_view.draw('Restart game?')
            self._state = 1
        elif self._state == 1:
            if self._confirmation_view.touch(event):
                if self._confirmation_view.value:
                    self._start_game()
                self._draw()
                self._state = 0

    def swipe(self, event):
        """Notify the application of a touchscreen swipe event."""
        moved = False

        if self._state == 0:
            if event[0] == wasp.EventType.UP:
                moved = self._shift(1,False)
            elif event[0] == wasp.EventType.DOWN:
                moved = self._shift(-1,False)
            elif event[0] == wasp.EventType.LEFT:
                moved = self._shift(1,True)
            elif event[0] == wasp.EventType.RIGHT:
                moved = self._shift(-1,True)

        if moved:
            self._add_tile()

    def _draw(self):
        """Draw the display from scratch."""
        board = self._board
        draw = wasp.watch.drawable
        draw.fill(GRID_BACKGROUND)
        draw.set_font(fonts.sans24)
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                self._update(draw, board[y][x], y, x)

    def _update(self, draw, cell, row, col):
        """Update the specified cell of the application display."""
        x = GRID_PADDING + (col * (CELL_SIZE + GRID_PADDING))
        y = GRID_PADDING + (row * (CELL_SIZE + GRID_PADDING))
        draw.set_color(CELL_FOREGROUND[cell], CELL_BACKGROUND[cell])
        draw.fill(CELL_BACKGROUND[cell], x, y, CELL_SIZE, CELL_SIZE)
        draw.string(CELL_LABEL[cell], x, y + 16, CELL_SIZE)

    def _start_game(self):
        """Start a new game."""
        self._board = self._create_board()
        self._add_tile()
        self._add_tile()

    def _create_board(self):
        """Create an empty 4x4 board."""
        board = []
        for _ in range(GRID_SIZE):
            board.append([0] * GRID_SIZE)
        return board

    def _add_tile(self):
        """Add a new tile to a random empty location on the board."""
        board = self._board
        randint = random.randint
        y = randint(0, GRID_SIZE-1)
        x = randint(0, GRID_SIZE-1)
        while board[y][x] != 0:
            y = randint(0, GRID_SIZE-1)
            x = randint(0, GRID_SIZE-1)
        board[y][x] = 1
        self._update(wasp.watch.drawable,1,y,x)

    def _shift(self, direction, orientation):
        """Shift and merge the tiles vertically."""
        draw = wasp.watch.drawable
        update = self._update
        board = self._board
        moved = False

        def read(y, x):
            if not orientation:
                y,x = x,y
            return board[y][x]

        def write(y, x, v):
            if not orientation:
                y,x = x,y

            board[y][x] = v
            update(draw, v, y, x)

        if direction > 0:
            s = 0 + 1
            e = GRID_SIZE
        else:
            s = GRID_SIZE - 1 - 1
            e = 0 - 1

        for y in range(GRID_SIZE):
            p = s - direction
            for x in range(s,e,direction):
                a = read(y,x)
                b = read(y,p)
                if a != 0:
                    if a == b:
                        write(y, p, a + 1)
                        write(y, x, 0)
                        moved = True
                        p += direction
                    else:
                        if b != 0:
                            p += direction
                        if x != p:
                            write(y, p, a)
                            write(y, x, 0)
                            moved = True
        return moved
