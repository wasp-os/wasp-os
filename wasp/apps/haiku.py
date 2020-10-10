# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 Daniel Thompson

"""Haiku viewer
~~~~~~~~~~~~~~~

These three lines poems are fun to write and fit nicely on a tiny screen.

If there is a file called haiku.txt in the flash filesystem then this app
allows it to be displayed three lines at a time using the pager.

This application also (optionally) loads an icon from the filesystem allowing
to be customized to match whether theme your verses are based around.
"""

import wasp
import icons

import io
import sys

from apps.pager import PagerApp

class HaikuApp(PagerApp):
    NAME = 'Haiku'

    def __init__(self):
        # Throw an exception if there is no poetry for us to read...
        open('haiku.txt').close()

        try:
            with open('haiku.rle', 'rb') as f:
                self.ICON = f.read()
        except:
            # Leave the default app icon if none is present
            pass

        super().__init__('')
        self._counter = -4

    def foreground(self):
        lines = []
        self._counter += 4

        with open('haiku.txt') as f:
            for i in range(self._counter):
                _ = f.readline()

            lines = [ '', ]
            for i in range(3):
                lines.append(f.readline())

            if len(lines[2]) == 0:
                self._counter = 0
                f.seek(0)
                lines = [ '', ]
                for i in range(3):
                    lines.append(f.readline())

        self._msg = '\n'.join(lines)

        super().foreground()
