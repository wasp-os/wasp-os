""" Real Time Clock based on the nRF-family low power counter """

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

    TODO: Maintain hh:mm:ss as an array so we can report time
          without memory allocation.
    """

    def __init__(self, counter):
        self.counter = counter
        self.uptime = 0
        self.set_time((12, 0, 0))

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

        self.ss += elapsed
        if self.ss >= 60:
            self.mm += self.ss // 60
            self.ss %= 60

            if self.mm >= 60:
                self.hh += self.mm // 60
                self.mm %= 60
                self.hh %= 24

        return True

    def set_time(self, t):
        self.lastcount = self.counter.counter()
        self.hh = t[0]
        self.mm = t[1]
        self.ss = t[2]

    def get_time(self):
        self.update()
        return (self.hh, self.mm, self.ss)
