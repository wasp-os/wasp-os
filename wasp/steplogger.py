# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 Daniel Thompson

"""Step logger
~~~~~~~~~~~~~~

Capture and record data from the step counter
"""

import array
import os
import time
import wasp

from micropython import const

TICK_PERIOD = const(6 * 60)
DUMP_LENGTH = const(5)
DUMP_PERIOD = const(DUMP_LENGTH * TICK_PERIOD)

class StepLogger:
    def __init__(self):
        self._data = array.array('H', (0,) * DUMP_LENGTH)
        self._steps = wasp.watch.accel.steps

        try:
            os.mkdir('logs')
        except:
            pass

        # Queue a tick
        self._t = int(wasp.watch.rtc.time()) // TICK_PERIOD * TICK_PERIOD
        wasp.system.set_alarm(self._t + TICK_PERIOD, self._tick)

    def _tick(self):
        """Capture the current step count in N minute intervals.

        The samples are queued in a small RAM buffer in order to reduce
        the number of flash access. The data is written out every few hours
        in a binary format ready to be reloaded and graphed when it is
        needed.
        """
        t = self._t

        # Work out where we are in the dump period
        i = t % DUMP_PERIOD // TICK_PERIOD

        # Get the current step count and record it
        steps = wasp.watch.accel.steps
        self._data[i] = steps - self._steps 
        self._steps = steps

        # Queue the next tick
        wasp.system.set_alarm(t + TICK_PERIOD, self._tick)
        self._t += TICK_PERIOD

        if i < (DUMP_LENGTH-1):
            return

        # Record the data in the flash
        walltime = time.localtime(t)
        yyyy = walltime[0]
        mm = walltime[1]
        dd = walltime[2]

        # Find when (in seconds) "today" started
        then = int(time.mktime((yyyy, mm, dd, 0, 0, 0, 0, 0, 0)))
        elapsed = t - then

        # Work out how dumps we expect to find in today's dumpfile
        dump_num = elapsed // DUMP_PERIOD

        # Update the log data
        try:
            os.mkdir('logs/' + str(yyyy))
        except:
            pass
        fname = 'logs/{}/{:02d}-{:02d}.steps'.format(yyyy, mm, dd)
        offset = dump_num * DUMP_LENGTH * 2
        try:
            sz = os.stat(fname)[6]
        except:
            sz = 0
        f = open(fname, 'ab')
        # This is a portable (between real Python and MicroPython) way to
        # grow the file to the right size.
        f.seek(min(sz, offset))
        for _ in range(sz, offset, 2):
            f.write(b'\x00\x00')
        f.write(self._data)
        f.close()

        # Wipe the data
        data = self._data
        for i in range(DUMP_LENGTH):
            data[i] = 0
