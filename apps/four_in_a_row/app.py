# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2023 Tony Robinson

"""Four in a Row
~~~~~~~~~~~~~~~~
 
This is the classic two player board game called Four In A Row or Connect4.  You play against the computer.

.. figure:: res/screenshots/FourInARowApp.png
    :width: 179

    Screenshot of Four In A Row

There is in intro/menu screen which has very brief instructions, allows you to set the opponent level and gives some stats on the number of games you have won.  Touching the screen sets the level from 0 to 6 which corresponds to the number of lookahead plies.  Swiping down enters the main game.  On your turn a red square counter will appear on the top row.  Touch the screen to move to the desired column, optionally touch again if you don't like your choice then swipe down to commit to playing that column.  The computer will reply with a yellow counter after a delay (dependent on level).  Your aim is to get four in a row before the computer does.  At end of game swipe down to return to the intro/menu screen.

This app is powered by a compact version of the Alpha Beta pruning algorithm.  For technical details see https://en.wikipedia.org/wiki/Connect_Four and https://kaggle.com/competitions/connectx/.  There isn't space for a transposition table in RAM, so MTDf isn't implmented, nevertheless it can play a challenging game.

"""

import wasp, array
from micropython import const

# parameters of the 'Four in a Row' game
_NROW    = const(6)
_NCOLUMN = const(7)
# assert _NCOLUMN == _NROW + 1 # need square, top row is where counters are placed
_NMIDDLE = const((_NCOLUMN - 1) // 2)
_NBOARD  = const(_NROW * _NCOLUMN)

# colours
_BLUE  = const(0x0010) # Blue: half way to full blue
_BLACK = const(0x0000) # Black
_cPLAY = const(0xF800) # Red: colour for human PLAYer - becuase I like playing red
_cCOMP = const(0xFFE0) # Yellow: colour for COMPputer pieces

# basics of the display
_NPIXEL  = const(240)
_NCELL   = const(_NPIXEL // _NCOLUMN)
_NBORDER = const((_NPIXEL - _NCELL * _NCOLUMN) // 2)
_NPAD    = const(2)

# states of game
_INTRO, _PLAY, _GAMEOVER = const(0), const(1), const(2)
_NLEVEL = const(7)

def _gameOver(bitmap):
    for s in [1, _NCOLUMN, _NCOLUMN+2, _NCOLUMN+1]:
        b = bitmap & (bitmap >> s)
        if b & (b >> 2 * s):
            return True
    return False

def _bitmapGet(bitmap, x, y):
    return (bitmap >> (y * (_NCOLUMN + 1) + x)) & 1

def _bitmapSet(bitmap, x, y):
    return bitmap | 1 << (y * (_NCOLUMN + 1) + x)

_searchOrder = bytearray(sorted(range(_NCOLUMN), key=lambda x:abs(x - _NMIDDLE)))

def _swapmin(bitNext, bitLast, low, depth, lob, upb):
    sumLow = sum(low)

    # list all the legal moves
    legal = [ n for n in _searchOrder if low[n] != _NROW ]
    
    # see if we can win                                                           
    for x in legal:
        if _gameOver(_bitmapSet(bitNext, x, low[x])):
            return (_NBOARD - sumLow + 1) // 2, x 

    # easy wins done, quit now if at search depth or end of board
    if depth == 0 or sumLow == _NBOARD:
        return 0, -1 # -1 is not right but DRAW will catch it

    # if can't win then see if we have to block                                                                     
    for x in legal:
        if _gameOver(_bitmapSet(bitLast, x, low[x])):
            legal = [ x ]
            break

    bestv = _NBOARD
    for x in legal:
        lowp = bytearray(low) # bytearray used as copy.copy()
        lowp[x] += 1
        v, _ = _swapmin(bitLast, _bitmapSet(bitNext, x, low[x]), lowp, depth-1, -upb, -lob)
        if v < bestv:
            bestv, bestx = v, x
            upb = min(upb, bestv)
            if bestv <= lob:
                break

    return -bestv, bestx

def rndColumn():
    return int(wasp.watch.rtc.uptime) % _NCOLUMN  # time used as RNG to save space

class FourInARowApp():
    NAME = '4 ina row'

    def __init__(self):
        self.screen = _INTRO
        self.level = wasp.widgets.Slider(_NLEVEL, x=10, y=150, color=_cPLAY)
        self.nwin  = array.array('H', [0] * _NLEVEL)
        self.ngame = array.array('H', [0] * _NLEVEL)

    def _showStats(self):
        nwin  = self.nwin[self.level.value]
        ngame = self.ngame[self.level.value]
        pc = int(100 * nwin / ngame + 0.5) if ngame > 0 else 0
        wasp.watch.drawable.string('level %d  won %d%%' % (self.level.value, pc), 0, 200, width=_NPIXEL)

    def _place(self, x, y, colour):
        wasp.watch.drawable.fill(x=_NBORDER + x*_NCELL + _NPAD, y=_NBORDER + (_NROW-y)*_NCELL + _NPAD, w=_NCELL - 2*_NPAD, h=_NCELL - 2*_NPAD, bg=colour)

    def foreground(self):
        draw = wasp.watch.drawable

        # draw board from state
        draw.fill()
        if self.screen == _INTRO:
            draw.string('FOUR IN A ROW', 0, 30, width=_NPIXEL)
            draw.string('Touch sets column', 0, 80, width=_NPIXEL)
            draw.string('swipe down to play', 0, 110, width=_NPIXEL)
            self.level.draw()
            self._showStats()
        else:
            draw.fill(x=0, y=_NBORDER+_NCELL, w=_NPIXEL, h=_NPIXEL-_NCELL, bg=_BLUE)
            for x in range(_NCOLUMN):
                for y in range(_NROW):
                    if _bitmapGet(self.bPLAY, x, y):
                        self._place(x, y, _cPLAY)
                    elif _bitmapGet(self.bCOMP, x, y):
                        self._place(x, y, _cCOMP)
            self._place(self.x, _NROW, _cPLAY)

        wasp.system.request_event(wasp.EventMask.TOUCH | wasp.EventMask.SWIPE_UPDOWN)

    # touch to set the drop column
    def touch(self, event):
        if self.screen == _INTRO:
            self.level.touch(event)
            self.level.update()
            self._showStats()
        elif self.screen == _PLAY:
            self._place(self.x, _NROW, _BLACK)
            self.x = min(max((event[1] - _NBORDER) // _NCELL, 0), _NCOLUMN-1)
            self._place(self.x, _NROW, _cPLAY)

    def _drop(self, x, colour):
        if self.low[x] == _NROW:
            wasp.watch.vibrator.pulse() # can't move here!
        else:
            y = self.low[x]
            for i in range(_NROW, y, -1):
                self._place(x, i-1, colour)
                self._place(x, i, _BLUE if i != _NROW else _BLACK)
                wasp.watch.time.sleep(0.1)
            if colour == _cPLAY:
                self.bPLAY = _bitmapSet(self.bPLAY, x, y)
            else:
                self.bCOMP = _bitmapSet(self.bCOMP, x, y)
            self.low[x] += 1

    # swipe down to drop, swipe left/right to exit
    def swipe(self, event):
        if event[0] == wasp.EventType.DOWN:
            if self.screen == _INTRO:
                self.x = _NMIDDLE
                self.bPLAY = 0
                self.bCOMP = 0
                self.low   = bytearray(_NCOLUMN)
                self.screen = _PLAY
                self.foreground()
                if self.ngame[self.level.value] % 2:
                    self._drop(rndColumn(), _cCOMP)
            elif self.screen == _PLAY and self.low[self.x] != _NROW:
                # play human PLAYer
                self._drop(self.x, _cPLAY)
                if _gameOver(self.bPLAY):
                    wasp.watch.drawable.string('YOU WIN!', 0, 0, width=_NPIXEL)
                    self.nwin[self.level.value] += 1
                    self.screen = _GAMEOVER
                    return

                if sum(self.low) < 3:
                    x = rndColumn()
                else:
                    depth = self.level.value + 1
                    if depth == 2 and sum(self.low) < 8:
                        depth += 1
                    v, x = _swapmin(self.bCOMP, self.bPLAY, self.low, depth, -_NBOARD, _NBOARD)
                self._drop(x, _cCOMP)
                    
                if _gameOver(self.bCOMP):
                    wasp.watch.drawable.string('YOU LOSE!', 0, 0, width=_NPIXEL)
                    self.screen = _GAMEOVER
                    return

                self._place(self.x, _NROW, _cPLAY)
            elif self.screen == _GAMEOVER:
                self.ngame[self.level.value] += 1
                self.screen = _INTRO
                self.foreground()
