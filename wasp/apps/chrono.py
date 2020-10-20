# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 David Diem
# based on clock.py by Daniel Thompson

import wasp
import math
import icons

clr = 0xffff
gry = 0x73ae
bgc = 0


class ChronoApp():

    NAME = 'Chrono'
    ICON = icons.clock
    
    def __init__(self):
        self.bp = 0
        self.bc = False
        self.acc = 0x07e0
#        self.z2 = [ 6, (0,15,0), (15,18,2), (15, 18, 3), (18, 21, 4), (21, 79, 5), (79, 82, 4), (82, 85, 3), (82, 85, 2), (85,100,0)] # nudelholz #
        self.z1 = ( 6,
                    (0,70,0),
                    (70,71,1),
                    (71,72,2),
                    (72,73,3),
                    (73,75,4), #
                    (75,77,4), #
                    (78,79,3),
                    (79,80,2),
                    (80,81,1),
                    (81,100,0)
        ) # lupe
        self.z1 = ( 6,
                    (0,100,0),
                    (100,101,1),
                    (101,102,4),
                    (102,103,6),
                    (103,104,7),
                    (104,106,8),
                    (106,107,8),                    
                    (107,108,8),
                    (108,110,7)                                        
        ) # lupe groß
        self.z2 = (6,
                    (0,15,0),
                    (15,18,2),
                    (15, 18, 3),
                    (18, 21, 4),
                    (21, 79, 5),
                    (68, 69, 0, self.acc, 3),
                    (58, 59, 0, self.acc, 3),                    
                    (79, 82, 4),
                    (82, 85, 3),
                    (82, 85, 2),
                    (85,100,0)) # nudelholz #
        

##handle event
        
    def foreground(self, effect=None):
        self.ons = ( -1, -1, -1, -1, -1, -1, -1, -1 )
        self.draw(effect)
#        wasp.system.request_event(wasp.Event.TOUCH | wasp.Event.SWIPE_UPDOWN)
        wasp.system.request_tick(1000)

    def tick(self, ticks):
        self.update()

    def background(self):
        pass

    def sleep(self):
        return True

    def wake(self):
        pass

    def mark(self, z, c, v, i, q, o, w, a, b):
        d = wasp.watch.drawable        
        for m in range(10*a,10*b,int(v*10)):
            n = math.radians(6/100*m-90)
            co = math.cos(n)
            si = math.sin(n)
            for p in range(i,o,q):
                d.fill(c, int(z[0]+co*p-w//2), int(z[1]+si*p-w//2), int(w), int(w))

    def hand(self, m, t, cy, c, l, w, r, s, prev):
        d = wasp.watch.drawable
        if cy == 0:
            an = 30*(t[3]+t[4]/60)
        else: # for 1 and 2
            an = 6*t[3+cy]
        o = math.cos(math.radians(an))
        i = math.sin(math.radians(an))                    
        ue = int(s[0]/100*l)
        if prev == True:
            try:
                if cy == 0:
                    anold = 30*(self.ons[3]+self.ons[4]/60)
                else: # for 1 and 2
                    anold = 6*self.ons[3+cy]
                oold = math.cos(math.radians(anold))
                iold = math.sin(math.radians(anold))
            except:
                pass
        oc = c
        for u in s[1:]:
            c = oc
            for p in range(int(-l*(u[0]-ue)/100),int(-l*(u[1]-ue)/100),-r):
                try:
                    c = u[3]
                    w = u[4]
                except:
                    pass
                of = int(u[2]*l/100) # normalize offset to length
                if prev:
                    d.fill(bgc, int(m[0]+of*oold-p*iold), int(m[1]+of*iold+p*oold), int(w), int(w))
                    d.fill(bgc, int(m[0]-of*oold-p*iold), int(m[1]-of*iold+p*oold), int(w), int(w))
                d.fill(c, int(m[0]+of*o-p*i), int(m[1]+of*i+p*o), int(w), int(w))
                d.fill(c, int(m[0]-of*o-p*i), int(m[1]-of*i+p*o), int(w), int(w))
    def ringM(self):
        now = wasp.watch.rtc.get_localtime()
        draw = wasp.watch.drawable
        self.hand((120, 120), now, 0, self.acc, 80, 2, 1, self.z2, True)
        self.hand((120, 120), now, 1, clr, 100, 2, 1, self.z2, True)
        self.hand((120, 120), now, 2, self.acc, 110, 1, 2, self.z1, True)
        self.mark((120, 120), gry, 50, 112, 1, 120, 5, 0, 600)
        self.mark((120, 120), gry, 10, 116, 1, 120, 1, 0, 600)#
        self.mark((120, 120), self.acc, 150, 112, 3, 120, 5, 0, 600)#
        self.ons = now        

    def ring9(self):
        now = wasp.watch.rtc.get_localtime()
        draw = wasp.watch.drawable
        self.mark((55,120), gry, 1, 35, 1, 36, 1, 0, 600)
        self.mark((55,120), gry, 85.7, 17, 1, 27, 1, -43, 557)#
        self.hand((55,120), (0,0,0,0, now[6]/7*60,0), 1, clr, 36, 1, 1, self.z2, True)
        self.ons = now        
        
    def ring6(self):
        now = wasp.watch.rtc.get_localtime()
        draw = wasp.watch.drawable
        self.mark((100,175), gry, 1, 30, 1, 31, 1, 0, 600)
        self.mark((100,175), gry, 85.7, 13, 1, 22, 1, -43, 557)#
        self.hand((100,175), (0,0,0,0, now[6]/7*60,0), 1, clr, 29, 1, 2, self.z1, True)
        self.ons = now        

    def ring12(self):
        now = wasp.watch.rtc.get_localtime()
        draw = wasp.watch.drawable
        self.mark((100,65), gry, 1, 30, 1, 31, 1, 0, 600)
        self.mark((100,65), gry, 85.7, 13, 1, 22, 1, -43, 557)#
        self.hand((100,65), (0,0,0,0, now[6]/7*60,0), 1, clr, 29, 1, 1, self.z2, True)
        self.ons = now        
        
        
                
                    
    def draw(self, effect=None):
        draw = wasp.watch.drawable
        draw.fill()
        self.on_screen = ( -1, -1, -1, -1, -1, -1 )
        self.ringM()
        self.ring9()        
        self.ring12()
        self.ring6()
        
    def update(self):
        now = wasp.watch.rtc.get_localtime()
        draw = wasp.watch.drawable
        if now[3] == self.ons[3] and now[4] == self.ons[4]:
            if now[5] != self.ons[5]:
                # every second
                self.hand((120, 120), now, 2, self.acc, 110, 1, 2, self.z1, True)
                if now[5] == now[3]*5+5:
                    self.hand((120, 120), now, 0, self.acc, 80, 2, 1, self.z2, True)
                if now[5] == now[4]+5:
                    self.hand((120, 120), now, 1, clr, 100, 2, 1, self.z2, True)
                if 28 <= now[5] <= 39:
                    self.ring6()
                elif 40 <= now[5] <= 51:
                    self.ring9()
                elif 51 <= now[5] or now[5] <= 2:
                    self.ring12()
                if self.bc != wasp.watch.battery.charging():
                    if wasp.watch.battery.charging():
                        a = self.acc
                    else:
                        a = gry
                    self.mark((55,120), a, 2, 36, 1, 37, 1, 0, 600)
                    self.mark((55,120), clr, 50, 35, 1, 36, 1, 0, 600)
                    self.bc = wasp.watch.battery.charging()
                self.ons = now
            return False
        # every minute
        self.ringM()
        self.ring12()
        self.ring9()
        self.ring6()
        

#batt
        self.ons = now
        return True
