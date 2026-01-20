# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2021 Daniel Thompson
"""Example of any automatically discovered application.

Any python file (``.py`` or ``.mpy``) discovered in the ``apps/``
directory will be automatically added to the Software application.
"""

import wasp

class ReadMeApp():
    NAME = "ReadMe"

    def foreground(self):
        draw = wasp.watch.drawable
        draw.fill()
        draw.string('Autoloaded from', 0, 96, width=240)
        draw.string('apps/read_me.py', 0, 96+32, width=240)
