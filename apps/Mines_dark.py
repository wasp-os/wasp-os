# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2023 sbot50
"""Mines application
~~~~~~~~~~~~~~~~~~~~~

Classic game of minesweeper.

Click once to reveal a tile
Click twice to flag a tile

flag all bombs to win!

.. figure:: res/MinesApp.png
    :width: 179
"""

import wasp
from random import seed, randint
from time import sleep
import fonts.sans18, fonts.sans24


class Mines_darkApp:
    NAME = "Mines"
    G = []
    S = B = C = L = 0
    T = [0, 0]
    
    def __init__(self):
        self.draw = wasp.watch.drawable

    def foreground(self):
        self.start()
        wasp.system.request_event(wasp.EventMask.TOUCH)
        wasp.system.request_tick(1)

    def start(self):
        self.B = wasp.watch.rtc.get_uptime_ms()
        seed(self.B)
        sample = [randint(0, 63) for j in range(10)]
        self.G = [0 if i not in sample else -1 for i in range(64)]
        self.G = [
            -1
            if self.G[i] == -1
            else sum(
                1
                for a in range(i // 8 - 1, i // 8 + 2)
                for b in range(i % 8 - 1, i % 8 + 2)
                if 0 <= a < 8 and 0 <= b < 8 and self.G[a * 8 + b] == -1
            )
            for i in range(64)
        ]
        self.draw.fill(0x0000)
        for i in range(64):
            self.draw.fill(0x2124, (i // 8) * 30 + 1, (i % 8) * 30 + 1, 28, 28)

    def touch(self, event):
        self.T = [event[1] // 30, event[2] // 30]
        self.C += 1
        self.L = wasp.watch.rtc.get_uptime_ms()

    def tick(self, ticks):
        i, j = self.T
        if self.S != 1:
            if wasp.watch.rtc.get_uptime_ms() - self.L >= 500:
                if self.C == 1 and self.G[i * 8 + j] != -3 and self.G[i * 8 + j] < 9:
                    if self.G[i * 8 + j] == -1:
                        self.draw_end(1)
                    elif self.G[i * 8 + j] >= 0:
                        self.draw_tile(i, j, self.G[i * 8 + j])
                elif self.C > 1:
                    if self.G[i * 8 + j] == -1:
                        self.G[i * 8 + j] = -3
                        self.draw.line(
                            i * 30 + 2,
                            j * 30 + 2,
                            (i + 1) * 30 - 3,
                            (j + 1) * 30 - 3,
                            3,
                            0x5801,
                        )
                        self.draw.line(
                            i * 30 + 2,
                            (j + 1) * 30 - 3,
                            (i + 1) * 30 - 3,
                            j * 30 + 2,
                            3,
                            0x5801,
                        )
                    elif self.G[i * 8 + j] == -3:
                        self.G[i * 8 + j] = -1
                        self.draw.fill(0x2124, i * 30 + 1, j * 30 + 1, 28, 28)
                    elif 0 <= self.G[i * 8 + j] <= 8:
                        self.G[i * 8 + j] += 9
                        self.draw.line(
                            i * 30 + 2,
                            j * 30 + 2,
                            (i + 1) * 30 - 3,
                            (j + 1) * 30 - 3,
                            3,
                            0x5801,
                        )
                        self.draw.line(
                            i * 30 + 2,
                            (j + 1) * 30 - 3,
                            (i + 1) * 30 - 3,
                            j * 30 + 2,
                            3,
                            0x5801,
                        )
                    elif self.G[i * 8 + j] >= 9:
                        self.G[i * 8 + j] -= 9
                        self.draw.fill(0x2124, i * 30 + 1, j * 30 + 1, 28, 28)
                if all(cell <= -2 for cell in self.G):
                    self.draw_end()
                self.C = self.L = 0
        else:
            if self.C == 1:
                self.S = self.C = 0
                self.start()

    def draw_tile(self, x, y, mines):
        self.G[x * 8 + y] = -2
        self.draw.set_color(0x8410, 0x10A2)
        self.draw.fill(0x10A2, x * 30 + 1, y * 30 + 1, 28, 28)
        self.draw.string(
            str(mines), x * 30 + 1, y * 30 + 5, 28
        ) if mines > 0 else self.reveal_tiles(x, y)

    def draw_end(self, defeat=0):
        self.S = 1
        self.draw.set_color(0x5801, 0x1082) if defeat else self.draw.set_color(
            0x01C4, 0x1082
        )
        self.draw.set_font(fonts.sans18)
        self.draw.string(
            str(round((wasp.watch.rtc.get_uptime_ms() - self.B) / 1000, 2))
            + " seconds",
            0,
            123,
            240,
        )
        self.draw.set_font(fonts.sans24)
        self.draw.string("Fail", 0, 99, 240) if defeat else self.draw.string(
            "Complete", 0, 99, 240
        )

    def reveal_tiles(self, x, y):
        self.G[x * 8 + y] = -2
        for i in range(x - 1, x + 2):
            for j in range(y - 1, y + 2):
                if 0 <= i < 8 and 0 <= j < 8 and 8 >= self.G[i * 8 + j] >= 0:
                    self.draw_tile(i, j, self.G[i * 8 + j])
                    sleep(0.01)
