"""Connect 4
    ~~~~~~~~~~~~
    
    Connect 4 is a 2 player game played on a 6x7 (height x width) grid.
    The players can choose in which column to drop a disc with their color,
    and when one of the players gets 4 adjacent discs in a row, column or diagonal, they win.
    
    Connect 4 is a solved game, meaning that in every case,
    by making the right move, the first player can win."""

import wasp
import array

class Connect4App():
    """Application implementing the classic Connect 4 game."""
    NAME = 'Connect 4'
    ROWS = 6
    COLUMNS = 7
    def __init__(self):
        """Initialize the app"""
        self._board = array.array('B', [0] * (6*7))
        self._color = 1 # 1 = red, 2 = yellow
    
    def foreground(self):
        """Activate the app"""
        self._draw()
        wasp.system.request_event(wasp.EventMask.TOUCH)

    def _draw(self):
        """Draw the display"""
        draw = wasp.watch.drawable
        draw.fill()
        for i in range(1, 7):
            draw.fill(i * (240//COLUMNS), 0, 1, 240) # fill vertical lines

        for i in range(1, 6):
            draw.fill(0, i * (240//ROWS), 240, 1)    # fill horizontal lines

        self._update()

    def _update(self):
        """Update dynamic parts of display (win message & discs)"""
        pass

    def touch(self, event):
        """Notify the app of a touchscreen touch"""
        pass
