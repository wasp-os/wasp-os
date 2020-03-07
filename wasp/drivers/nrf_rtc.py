""" Real Time Clock based on the nRF-family low power counter """

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
    """Real Time Clock based on the nRF-family low power counter."""

    def __init__(self, counter):
        self.counter = counter
        self.uptime = 0
        self.set_localtime((2020, 2, 18, 12, 0, 0, 0, 0))

    def update(self):
        newcount = self.counter.counter()
        split = newcount - self.lastcount
        if split == 0:
            return False
        if split < 0:
            split += (1 << 24)
        elapsed = split // 8
        self.lastcount += elapsed * 8 
        self.lastcount &= (1 << 24) - 1   

        self.uptime += elapsed
        return True

    def set_localtime(self, t):
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
        self.offset = lt - self.uptime

    def get_localtime(self):
        self.update()
        return time.localtime(self.offset + self.uptime)

    def get_time(self):
        localtime = self.get_localtime()
        return localtime[3:6]

    def get_uptime_ms(self):
        """Return the current uptime in milliseconds."""
        return self.uptime * 1000
