"""Connect 4
    ~~~~~~~~~~~~
    
    Connect 4 is a 2 player game played on a 6x7 (height x width) grid.
    The players can choose in which column to drop a disc with their color,
    and when one of the players gets 4 adjacent discs in a row, column or diagonal, they win.
    
    Connect 4 is a solved game, meaning that in every case,
    by making the right move, the first player can win."""

import wasp
import array
import draw565


class Connect4App():
    """Application implementing the classic Connect 4 game."""
    NAME = 'Connect4'
    ROWS = 6
    COLUMNS = 7
    MODES = ('Playing', 'Win', 'Draw')

    def __init__(self):
        """Initialize the app"""
        self._board = array.array('B', [0] * (6*7))
        self._color = 1 # 1 = red(0xF800), 2 = yellow(0xFFC0)
        self._mode = 'Playing'
    
    def foreground(self):
        """Activate the app"""
        self._draw()
        wasp.system.request_event(wasp.EventMask.TOUCH)

    def _draw(self):
        """Draw the display"""
        draw = wasp.watch.drawable
        draw.fill()
        if self._mode == 'Playing':
            for i in range(1, 7):
                draw.fill(None, i * (240//self.COLUMNS), 0, 1, 240) # fill vertical lines

            for i in range(1, 6):
                draw.fill(None, 0, i * (240//self.ROWS), 240, 1)    # fill horizontal lines

            self._update()


    def _update(self):
        """Update dynamic parts of display (win message & discs)"""
        for y in range(6):
            for x in range(7):
                i = x + y * 7
                if self._board[i] == 0:
                    continue
                dx = (x * 240) // 7
                dy = (y * 240) // 6
                color = 0xF800 if self._board[i] == 1 else 0xFFC0
                wasp.watch.drawable.fill(color, dx, dy, 240//self.COLUMNS, 240//self.ROWS)

    def touch(self, event):
        """Notify the app of a touchscreen touch"""
        if self._mode == 'Playing':
            column = (self.COLUMNS * event[1]) // 240
            disks_in_column = 0
            first_free_place = None
            # Count the amount of disks in the column we want.
            # If it's full, we'll ignore the event
            for i in range(35, -1, -7):
                if self._board[i + column] != 0:
                    disks_in_column += 1
                else:
                    first_free_place = (i + column) if first_free_place is None else first_free_place

            if disks_in_column >= 6:
                return # column is full, can't place piece here!

            self._board[first_free_place] = self._color
            self._color = 3 - self._color # yellow(2) => red(1), red(1) => yellow(2)
            self._update()

        
