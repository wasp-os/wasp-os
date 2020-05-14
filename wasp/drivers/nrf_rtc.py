# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 Daniel Thompson

"""nRF-family RTC driver
~~~~~~~~~~~~~~~~~~~~~~~~
"""

import machine
import time

#class Stim(object):
#    def __init__(self):
#        self(0)
#
#    def __call__(self, v):
#        self.c = v
#    
#    def counter(self):
#        return self.c

class RTC(object):
    """Real Time Clock based on the nRF-family low power counter.

    .. automethod:: __init__
    """

    def __init__(self, counter):
        """Wrap an RTCounter to provide a fully fledged Real Time Clock.

        If the PNVRAM is valid then we use it to initialize the RTC otherwise
        we just make something up.

        :param RTCounter counter: The RTCCounter channel to adopt.
        """
        self.counter = counter

        if machine.mem32[0x200039c0] == 0x1abe11ed and \
           machine.mem32[0x200039dc] == 0x10adab1e:
            self.lastcount = self.counter.counter()
            self.offset = machine.mem32[0x200039c4]
            self._uptime = machine.mem32[0x200039c8] // 125
        else:
            machine.mem32[0x200039c0] = 0x1abe11ed
            machine.mem32[0x200039dc] = 0x10adab1e
            self._uptime = 0
            self.set_localtime((2020, 3, 1, 3, 0, 0, 0, 0))

    def update(self):
        """Check for counter updates.

        :returns: True of the wall time has changed, False otherwise.
        """
        newcount = self.counter.counter()
        split = newcount - self.lastcount
        if split == 0:
            return False
        if split < 0:
            split += (1 << 24)

        self.lastcount += split
        self.lastcount &= (1 << 24) - 1   
        self._uptime += split
        machine.mem32[0x200039c8] = self._uptime * 125

        return True

    def set_localtime(self, t):
        """Set the current wall time.

        :param sequence t:
                Wall time formatted as (yyyy, mm, dd, HH, MM, SS), any
                additional elements in sequence will be ignored.
        """
        self.lastcount = self.counter.counter()

        if len(t) < 8:
            yyyy = t[0]
            mm = t[1]
            dd = t[2]
            HH = t[3]
            MM = t[4]
            SS = t[5]

            t = (yyyy, mm, dd, HH, MM, SS, 0, 0)

        lt = time.mktime(t)
        self.offset = lt - (self._uptime >> 3)
        machine.mem32[0x200039c4] = self.offset

    def get_localtime(self):
        """Get the current time and date.

        :returns: Wall time formatted as (yyyy, mm, dd, HH, MM, SS, wday, yday)
        """
        self.update()
        return time.localtime(self.offset + (self._uptime >> 3))

    def get_time(self):
        """Get the current time.

        :returns: Wall time formatted as (HH, MM, SS)
        """
        localtime = self.get_localtime()
        return localtime[3:6]

    @property
    def uptime(self):
        """Provide the current uptime in seconds."""
        return self._uptime // 8

    def get_uptime_ms(self):
        """Return the current uptime in milliseconds."""
        return self._uptime * 125
