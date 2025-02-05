# SPDX-License-Identifier: MIT
# Copyright (C) 2023 Eloi Torrents
"""Puzzle 15
~~~~~~~~~~~~

A popular sliding block puzzle game.

    .. figure:: res/screenshots/Puzzle15App.png
        :width: 179

        Screenshot of the 15 puzzle application
"""

import wasp
import widgets
import random
import fonts
from micropython import const

_FONT = fonts.sans24
_GRID_SIZE = const(4)
_GRID_PADDING = const(8)
_GRID_BACKGROUND = const(0x942F)
_EMPTY_BACKGROUND = const(0x9CB1)
_CELL_BACKGROUND = const(0xEF19)
_CELL_FOREGROUND = const(0x736C)

_SCREEN_SIZE = const(240)
_CELL_SIZE = const((_SCREEN_SIZE - (_GRID_PADDING * (_GRID_SIZE + 1))) // _GRID_SIZE)

# 2-bit RLE, 96x64, generated from res/icons/puzzle_15_icon.png, 566 bytes
icon = (
    b'\x02'
    b'`@'
    b'\x10\xbf\x01 \xbf\x01 \xbf\x01 \x83@\xfaM\x82M'
    b'\x82M\x82M\x83 \x83M\x82M\x82M\x82M\x83 '
    b'\x83M\x82M\x82M\x82M\x83 \x83M\x82M\x82M'
    b'\x82M\x83 \x83M\x82M\x82M\x82M\x83 \x83M'
    b'\x82M\x82M\x82M\x83 \x83M\x82M\x82M\x82M'
    b'\x83 \x83M\x82M\x82M\x82M\x83 \x83M\x82M'
    b'\x82M\x82M\x83 \x83M\x82M\x82M\x82M\x83 '
    b'\x83M\x82M\x82M\x82M\x83 \x83M\x82M\x82M'
    b'\x82M\x83 \x83M\x82M\x82M\x82M\x83 \xbf\x01'
    b' \xbf\x01 \x83M\x82M\x82M\x82M\x83 \x83M'
    b'\x82M\x82M\x82M\x83 \x83M\x82M\x82M\x82M'
    b'\x83 \x83M\x82M\x82M\x82M\x83 \x83M\x82M'
    b'\x82M\x82M\x83 \x83M\x82M\x82M\x82M\x83 '
    b'\x83M\x82M\x82M\x82M\x83 \x83M\x82M\x82M'
    b'\x82M\x83 \x83M\x82M\x82M\x82M\x83 \x83M'
    b'\x82M\x82M\x82M\x83 \x83M\x82M\x82M\x82M'
    b'\x83 \x83M\x82M\x82M\x82M\x83 \x83M\x82M'
    b'\x82M\x82M\x83 \xbf\x01 \xbf\x01 \x83M\x82M'
    b'\x82M\x82M\x83 \x83M\x82M\x82M\x82M\x83 '
    b'\x83M\x82M\x82M\x82M\x83 \x83M\x82M\x82M'
    b'\x82M\x83 \x83M\x82M\x82M\x82M\x83 \x83M'
    b'\x82M\x82M\x82M\x83 \x83M\x82M\x82M\x82M'
    b'\x83 \x83M\x82M\x82M\x82M\x83 \x83M\x82M'
    b'\x82M\x82M\x83 \x83M\x82M\x82M\x82M\x83 '
    b'\x83M\x82M\x82M\x82M\x83 \x83M\x82M\x82M'
    b'\x82M\x83 \x83M\x82M\x82M\x82M\x83 \xbf\x01'
    b' \xbf\x01 \x83M\x82M\x82M\x82\x80\x81\x8d\xc0\xdb'
    b'\xc3 \xc3M\xc2M\xc2M\xc2\x8d\xc3 \xc3M\xc2M'
    b'\xc2M\xc2\x8d\xc3 \xc3M\xc2M\xc2M\xc2\x8d\xc3 '
    b'\xc3M\xc2M\xc2M\xc2\x8d\xc3 \xc3M\xc2M\xc2M'
    b'\xc2\x8d\xc3 \xc3M\xc2M\xc2M\xc2\x8d\xc3 \xc3M'
    b'\xc2M\xc2M\xc2\x8d\xc3 \xc3M\xc2M\xc2M\xc2\x8d'
    b'\xc3 \xc3M\xc2M\xc2M\xc2\x8d\xc3 \xc3M\xc2M'
    b'\xc2M\xc2\x8d\xc3 \xc3M\xc2M\xc2M\xc2\x8d\xc3 '
    b'\xc3M\xc2M\xc2M\xc2\x8d\xc3 \xff\x01 \xff\x01 '
    b'\xff\x01\x10'
)

class Puzzle15App():
    """Let's solve the 15 puzzle."""
    NAME = '15'
    ICON = icon

    def __init__(self):
        """Initialize the application."""
        self._state = 0
        self._confirmation_view = widgets.ConfirmationView()
        self._start_game()

    def foreground(self):
        """Activate the application."""
        wasp.system.request_event(wasp.EventMask.TOUCH |
                                  wasp.EventMask.SWIPE_UPDOWN |
                                  wasp.EventMask.SWIPE_LEFTRIGHT)

        self._state = 0
        self._draw()

    def touch(self,event):
        """Notify the application of a touchscreen touch event."""
        if self._state == 0:
            self._confirmation_view.draw("{} Moves. Again?".format(self._move_count))
            self._state = 1
        elif self._state == 1:
            if self._confirmation_view.touch(event):
                if self._confirmation_view.value:
                    self._start_game()
                self._draw()
                self._state = 0

    def swipe(self, event):
        """Notify the application of a touchscreen swipe event."""
        draw = wasp.watch.drawable
        if self._state == 0:
            move_x, move_y = 0, 0
            if event[0] == wasp.EventType.LEFT and self._empty_y < _GRID_SIZE - 1:
                move_y = 1
            elif event[0] == wasp.EventType.RIGHT and self._empty_y > 0:
                move_y = -1
            elif event[0] == wasp.EventType.UP and self._empty_x < _GRID_SIZE - 1:
                move_x = 1
            elif event[0] == wasp.EventType.DOWN and self._empty_x > 0:
                move_x = -1
            if move_x != 0 or move_y !=0:
                x, y, b = self._empty_x, self._empty_y, self._board
                b[x][y], b[x + move_x][y + move_y] = b[x + move_x][y + move_y], b[x][y] 
                self._empty_x += move_x
                self._empty_y += move_y
                self._move_count += 1
                self._update(draw, x, y)
                self._update(draw, self._empty_x, self._empty_y)

    def _draw(self):
        """Draw the display from scratch."""
        draw = wasp.watch.drawable
        draw.fill(_GRID_BACKGROUND)
        draw.set_font(_FONT)
        for y in range(_GRID_SIZE):
            for x in range(_GRID_SIZE):
                self._update(draw, y, x)

    def _update(self, draw, row, col):
        """Update the specified cell of the application display."""
        x = _GRID_PADDING + (col * (_CELL_SIZE + _GRID_PADDING))
        y = _GRID_PADDING + (row * (_CELL_SIZE + _GRID_PADDING))
        if self._board[row][col] != 0:
            draw.set_color(_CELL_FOREGROUND, _CELL_BACKGROUND)
            draw.fill(_CELL_BACKGROUND, x, y, _CELL_SIZE, _CELL_SIZE)
            draw.string(str(self._board[row][col]), x, y + 16, _CELL_SIZE)
        else:
            draw.fill(_EMPTY_BACKGROUND, x, y, _CELL_SIZE, _CELL_SIZE)

    def _start_game(self):
        """Start a new game."""
        self._board = self._create_board()
        self._empty_x = _GRID_SIZE - 1
        self._empty_y = _GRID_SIZE - 1
        self._move_count = 0

    def _get_invCount(self, board):
        """Count inversion count.
        https://www.geeksforgeeks.org/check-instance-15-puzzle-solvable/"""
        num_list = [num for row in board for num in row]
        inv_count = 0
        for i, num1 in enumerate(num_list[:-2]):
            for num2 in num_list[i+1:-1]:
                if num1 > num2:
                    inv_count += 1
        return inv_count

    def _getNum(self, v):
        """return the next random number"""
        n = len(v)
        idx = random.randint(0, n-1)
        num, v[idx] = v[idx], v[n-1]
        v.pop()
        return num

    def _create_board(self):
        """Create a new GRID_SIZE x GRID_SIZE board."""
        board = [[0] * _GRID_SIZE for _ in range(_GRID_SIZE)]
        v = list(range(1, _GRID_SIZE * _GRID_SIZE))
        for i in range(_GRID_SIZE):
            for j in range(_GRID_SIZE):
                if i != _GRID_SIZE - 1 or j != _GRID_SIZE -1: 
                    board[i][j] = self._getNum(v)
        # Ensure solvability
        if self._get_invCount(board) % 2 == 1:
            board[-1][-3], board[-1][-2] = board[-1][-2], board[-1][-3]
        return board
