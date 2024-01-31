# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 Johannes Wache, 2023 Samuel Sloniker

import wasp
import fonts
import time

display = [
    [
        [
            "key:ej0",
            "key:tq1",
            "key:ax2",
            "key:oz3",
            "key:iw4",
            "key:np5",
            "key:sv6",
            "key:rf7",
            "key:lg8",
            "key:dk9",
            "action:shift",
            "key:cm,",
            "key:hb.",
            "key:uy?",
            "action:sym",
            "action:barr",
            "action:bdel",
            "key: ",
            "action:fdel",
            "action:farr",
        ],
        [
            "ej0",
            "tq1",
            "ax2",
            "oz3",
            "iw4",
            "np5",
            "sv6",
            "rf7",
            "lg8",
            "dk9",
            "***",
            "cm,",
            "hb.",
            "uy?",
            "(!)",
            "<",
            "<x",
            "_",
            "x>",
            ">",
        ],
    ],
    [
        [
            "key:!|",
            "key::;",
            "key:~`",
            'key:"(',
            "key:')",
            "key:&",
            "key:@[",
            "key:#]",
            "key:${",
            "key:%}",
            "key:*^",
            "key:/\\",
            "key:+-",
            "key:=_",
            "action:sym",
            "action:barr",
            "action:bdel",
            "key: ",
            "action:fdel",
            "action:farr",
        ],
        [
            "!|",
            ":;",
            "~`",
            '"(',
            "')",
            "&",
            "@[",
            "#]",
            "${",
            "%}",
            "*^",
            "/\\",
            "+-",
            "=_",
            "abc",
            "<",
            "<x",
            "_",
            "x>",
            ">",
        ],
    ],
]


class Keyboard:
    def __init__(self, callback):
        self._callback = callback
        self.is_open = False

    def open(self):
        self._last = ""
        self._count = None
        self._last_time = 0
        self._string = ""
        self._string_after = ""
        self._cap_mode = 0
        self._screen = 0
        self.is_open = True
        self._draw()

    def draw(self):
        if self.is_open:
            self._draw()
            return True
        else:
            return False

    def touch(self, event):
        if self.is_open:
            self._touch(event)
            return True
        else:
            return False

    def _touch(self, event):
        x = event[1] // 47
        y = (event[2] // 48) - 1

        # Error handling for touching at the border
        if x > 4:
            x = 4
        if y > 3:
            y = 3

        if y == -1:
            if x == 4:
                self.is_open = False
                self._callback(self._string + self._string_after)
            else:
                pass
        else:
            cat, value = display[self._screen][0][x + 5 * y].split(":", 1)

            if cat == "key":
                if (
                    self._cap_mode
                    or self._last.lower() == value
                    and 'A' <= self._last[0] <= 'Z'
                ):
                    value = value.upper()

                if self._cap_mode == 1:
                    self._cap_mode = 0
                    self._draw()

                if (time.time() - self._last_time) <= 1 and self._last == value:
                    self._count = (self._count + 1) % len(value)
                    self._string = self._string[:-1] + value[self._count]
                else:
                    self._last = value
                    self._count = 0
                    self._string += value[self._count]
                self._last_time = time.time()
                self._display_string()
            else:
                if value == "bdel":
                    self._string = self._string[:-1]
                    self._display_string()
                elif value == "fdel":
                    self._string_after = self._string_after[1:]
                    self._display_string()
                elif value == "barr":
                    self._string_after = self._string[-1] + self._string_after
                    self._string = self._string[:-1]
                    self._display_string()
                elif value == "farr":
                    self._string = self._string + self._string_after[:1]
                    self._string_after = self._string_after[1:]
                    self._display_string()
                elif value == "shift":
                    self._cap_mode = (self._cap_mode + 1) % 3
                    self._draw()
                    self._last = ""
                    self._count = None
                    self._last_time = 0
                elif value == "sym":
                    self._cap_mode = 0
                    self._screen = (self._screen + 1) % len(display)
                    self._draw()

    def _display_string(self):
        draw = wasp.watch.drawable
        theme = wasp.system.theme
        hi = theme("bright")
        draw.set_color(hi)

        # TODO: make sure cursor is on screen
        string = f"{self._string}|{self._string_after}"
        boundaries = draw.wrap("".join(reversed(string)), 194, False)
        draw.string(
            string[0 - boundaries[1] :],
            0,
            10,
            width=196,
            right=True,
        )

    def _draw_grid(self, draw, top_bar_bg, grid_bg, line_color):
        # Draw the background
        draw.fill(top_bar_bg, 0, 0, 240, 48)
        draw.fill(grid_bg, 0, 48, 240, 236 - 48)

        # Make grid:
        draw.set_color(line_color)
        for i in range(4):
            # horizontal lines
            draw.line(x0=0, y0=(i + 1) * 47, x1=239, y1=(i + 1) * 47)
            # vertical lines
            draw.line(x0=(i + 1) * 47, y0=47, x1=(i + 1) * 47, y1=235)
        draw.line(x0=0, y0=47, x1=0, y1=236)
        draw.line(x0=239, y0=47, x1=239, y1=236)
        draw.line(x0=0, y0=236, x1=239, y1=236)

    def _draw(self):
        draw = wasp.watch.drawable
        theme = wasp.system.theme

        hi = theme("bright")
        lo = theme("mid")
        mid = draw.lighten(lo, 2)
        bg = draw.darken(theme("ui"), theme("contrast"))
        bg2 = draw.darken(bg, 2)

        self._draw_grid(draw, 0, bg2, lo)

        # Draw button display[self._screen][1]
        draw.set_color(hi)
        draw.string(">", 215, 10)
        draw.set_color(hi, bg2)
        draw.set_font(fonts.sans18)

        try:
            display[self._screen][1][
                display[self._screen][0].index("action:shift")
            ] = ["lc", "Ca", "CL"][self._cap_mode]
        except ValueError:
            pass

        for x in range(5):
            for y in range(4):
                key = x + 5 * y
                label = display[self._screen][1][key]
                if self._cap_mode and display[self._screen][0][key].startswith(
                    "key:"
                ):
                    if self._cap_mode == 1:
                        label = label[0].upper() + label[1:]
                    else:
                        label = label.upper()
                draw.string(label, x * 47 + 1, y * 47 + 60, 46)

        draw.set_color(hi)
        self._display_string()
