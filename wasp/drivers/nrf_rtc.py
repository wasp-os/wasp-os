# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 Daniel Thompson

"""nRF-family RTC driver
~~~~~~~~~~~~~~~~~~~~~~~~
"""

import machine
import micropython
import time

from micropython import const

_DAY_TICKS = const(8 * 24 * 60 * 60)

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

    def __init__(self, counter, default=(2020, 3, 1, 3, 0, 0, 0, 0)):
        """Wrap an RTCounter to provide a fully fledged Real Time Clock.

        If the PNVRAM is valid then we use it to initialize the RTC otherwise
        we fall back to the default time (the time of the build is a good
        choice: it is the earliest the watch can possibly be running).

        :param RTCounter counter: The RTCCounter channel to adopt.
        :param sequence default:  Wall time to start from after a cold boot,
                                  formatted as (yyyy, mm, dd, HH, MM, SS, ...)
        """
        self.counter = counter

        # The PNVRAM holds the wall time as an offset plus a millisecond
        # counter, which the bootloader increments while it runs. mem32
        # reads the counter as a signed value, so it must stay well below
        # 2**31 ms (24 days): whole days of uptime are moved into the
        # offset (see update()), and _base is the part moved since boot.
        self._base = 0
        if machine.mem32[0x200039c0] == 0x1abe11ed and \
           machine.mem32[0x200039dc] == 0x10adab1e:
            self.lastcount = self.counter.counter()
            # Older firmware let the counter grow without limit
            ticks = (machine.mem32[0x200039c8] & 0xffffffff) // 125
            # Uptime counts from this boot: the time before it goes into
            # the offset
            self.offset = machine.mem32[0x200039c4] + (ticks >> 3)
            self._uptime = ticks & 7
            machine.mem32[0x200039c4] = self.offset
            machine.mem32[0x200039c8] = self._uptime * 125
        else:
            machine.mem32[0x200039c0] = 0x1abe11ed
            machine.mem32[0x200039dc] = 0x10adab1e
            self._uptime = 0
            self.set_localtime(default)

    @micropython.native
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
        uptime = self._uptime
        uptime += split
        self._uptime = uptime
        uptime -= self._base
        while uptime >= _DAY_TICKS:
            self._base += _DAY_TICKS
            uptime -= _DAY_TICKS
            machine.mem32[0x200039c4] = self.offset + (self._base >> 3)
        machine.mem32[0x200039c8] = uptime * 125

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
        machine.mem32[0x200039c4] = self.offset + (self._base >> 3)

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

    @micropython.native
    def time(self):
        """Get time in the same format as time.time"""
        return self.offset + (self._uptime >> 3)

    @property
    def uptime(self):
        """Provide the time since the watch started, in seconds."""
        return self._uptime // 8

    @micropython.native
    def get_uptime_ms(self):
        """Return the current uptime in milliseconds."""
        return self._uptime * 125
