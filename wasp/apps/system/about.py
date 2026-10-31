# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Michiel W. Beijen

"""About
~~~~~~~~

Shows which version of wasp-os is running, together with the board, the
MicroPython version, the uptime, the battery voltage and how much RAM and
flash are free. Handy to include in a bug report.

.. figure:: res/screenshots/AboutApp.png
    :width: 179

The version comes from ``git describe`` when the firmware is built, so a
build made between releases shows how many commits it is past the last
release, and the commit it was built from.
"""

import wasp
import fonts
import gc
import icons
import os
import sys

try:
    from version import VERSION
except ImportError:
    VERSION = 'unknown'

def _uptime(secs):
    """Format seconds as 1d 02:03 or 02:03:04."""
    mins, secs = divmod(secs, 60)
    hours, mins = divmod(mins, 60)
    days, hours = divmod(hours, 24)
    if days:
        return '{}d {:02d}:{:02d}'.format(days, hours, mins)
    return '{:02d}:{:02d}:{:02d}'.format(hours, mins, secs)

def _kb(n):
    return '{} KB'.format(n // 1024)

class AboutApp():
    """Show the version of wasp-os and some facts about the watch."""
    NAME = 'About'
    ICON = icons.about

    def foreground(self):
        """Activate the application."""
        self._draw()

    def _facts(self):
        """The board, and the rows to show as (label, value) pairs."""
        if sys.implementation.name == 'micropython':
            uname = os.uname()
            board = uname.machine.split(' with ')[0]
            python = ('MicroPython', uname.release)
            # The filesystem is mounted at /flash; / is an empty root
            st = os.statvfs('/flash')
            flash = _kb(st[0] * st[4])
        else:
            board = 'Simulator'
            python = ('Python', sys.version.split()[0])
            flash = '-'

        gc.collect()
        ram = _kb(gc.mem_free()) if hasattr(gc, 'mem_free') else '-'
        mv = wasp.watch.battery.voltage_mv()

        return board, (
            python,
            ('Uptime', _uptime(int(wasp.watch.rtc.uptime))),
            ('Battery', '{}.{:02d} V'.format(mv // 1000, mv % 1000 // 10)),
            ('RAM free', ram),
            ('Flash free', flash),
        )

    def _draw(self):
        """Draw the display from scratch."""
        draw = wasp.watch.drawable
        hi = wasp.system.theme('bright')
        lo = wasp.system.theme('mid')
        board, rows = self._facts()
        draw.fill()

        draw.set_color(hi)
        draw.set_font(fonts.sans24)
        draw.string('wasp-os', 0, 8, width=240)
        draw.set_font(fonts.sans18)
        draw.string(VERSION, 0, 42, width=240)
        draw.set_color(lo)
        draw.string(board, 0, 64, width=240)

        y = 100
        for label, value in rows:
            draw.set_color(lo)
            draw.string(label, 8, y)
            draw.set_color(hi)
            draw.string(value, 232 - draw.bounding_box(value)[0], y)
            y += 27
