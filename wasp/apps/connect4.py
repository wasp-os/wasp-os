"""Connect 4
   ~~~~~~~~~~~~~
    
    Connect 4 is a 2 player game played on a 6x7 (height x width) grid.
    The players can choose in which column to drop a disc with their color,
    and when one of the players gets 4 adjacent discs in a row, column or diagonal, they win.
    
    Connect 4 is a solved game, meaning that in every case,
    by making the right move, the first player can win."""

import wasp
import array
import draw565

def all(arr, val):
    """Returns true if all of arr equals to val"""
    for x in arr:
        if x != val:
            return False
    return True

class Connect4App():
    """Application implementing the classic Connect 4 game."""
    NAME = 'Connect4'
    ROWS = 6
    COLUMNS = 7
    MODES = ('Playing', 'Win', 'Draw')

    def __init__(self):
        """Initialize the app"""
        self._initialize()
    
    def _initialize(self):
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
                draw.fill(None, i * (240//self.COLUMNS), 0, 2, 240) # fill vertical lines

            for i in range(1, 6):
                draw.fill(None, 0, i * (240//self.ROWS), 240, 2)    # fill horizontal lines

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
                wasp.watch.drawable.fill(color, dx+1, dy+1, 240//self.COLUMNS-1, 240//self.ROWS-1)
        if self._mode == 'Win':
            wasp.watch.drawable.string(f'{"Red" if self._color == 2 else "Yellow"} won!', 0, 0, 240)
        elif self._mode == 'Draw':
            wasp.watch.drawable.string('Draw!', 0, 0, 240)
        if self._mode == 'Win' or self._mode == 'Draw':
            wasp.watch.drawable.string('touch to restart', 0, 30, 240)


    def _is_win(self, row, col):
        """Returns 0 if nobody won, and 1 or 2 if a player has won."""
        def slice_column(arr, col):
            return arr[col:42:7]
        def slice_row(arr, row):
            return arr[row*7:(row+1)*7]
        row_slices = ( slice(0, 4),
                       slice(1, 5),
                       slice(2, 6),
                       slice(3, 7) )
        col_slices = ( slice(0, 4),
                       slice(1, 5),
                       slice(2, 6) )
        diagonals = ( slice(0, 41, 8),
                      slice(1, 42, 8),
                      slice(2, 35, 8),
                      slice(3, 28, 8),
                      slice(3, 21, 6),
                      slice(4, 29, 6),
                      slice(5, 36, 6),
                      slice(6, 37, 6),
                      slice(7, 40, 8),
                      slice(13, 38, 6),
                      slice(14, 39, 8),
                      slice(20, 39, 6) )

        crow = slice_row(self._board, row)
        ccol = slice_column(self._board, col)
        for s in row_slices:
            if all(crow[s], 1):
                return 1
            elif all(crow[s], 2):
                return 2
        for s in col_slices:
            if all(ccol[s], 1):
                return 1
            elif all(ccol[s], 2):
                return 2
        for s in diagonals:
            diagonal = self._board[s]
            l = len(diagonal)
            slices = ( slice(0, 4), )
            if l > 4:
                slices += (slice(1, 5),)
            if l > 5:
                slices += (slice(2, 6),)
            for sl in slices:
                if all(diagonal[sl], 1):
                    return 1
                elif all(diagonal[sl], 2):
                    return 2
        return 0

    def screen_to_world_matrix(self, x, y):
        """Converts pixels to game grid"""
        return ((x * self.COLUMNS) // 240, (y * self.ROWS) // 240)

    def touch(self, event):
        """Notify the app of a touchscreen touch"""
        if self._mode == 'Playing':
            column, row = self.screen_to_world_matrix(event[1], event[2])
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

            row = first_free_place//7

            self._board[first_free_place] = self._color
            self._color = 3 - self._color # yellow(2) => red(1), red(1) => yellow(2)
            self._update()
            is_win = self._is_win(row, column) != 0
            if is_win:
                self._mode = 'Win'
                self._update()
            elif 0 not in self._board:
                self._mode = 'Draw'
                self._update()
        elif self._mode == 'Win' or self._mode == 'Draw':
            self._initialize()
            self._draw()
        
