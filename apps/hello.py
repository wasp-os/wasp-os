# SPDX-License-Identifier: MY-LICENSE
# Copyright (C) YEAR(S), AUTHOR

import wasp

class HelloApp():
    """A hello world application for wasp-os."""
    NAME = "Hello"

    def __init__(self, msg="Hello, world!"):
        self.msg = msg

    def foreground(self):
        self._draw()

    def _draw(self):
        draw = wasp.watch.drawable
        draw.fill()
        draw.string(self.msg, 0, 108, width=240)
