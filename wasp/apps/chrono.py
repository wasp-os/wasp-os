# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 David Diem
# based on clock.py by Daniel Thompson

import wasp
import math # needed for cosine and sine functions
import icons

clr = 0xffff # main color
gry = 0x73ae # grey
bgc = 0 # background color


class ChronoApp():

    NAME = 'Chrono'
    ICON = icons.clock
    
    def __init__(self):
        self.bp = 0 # battery percentage
        self.bc = False # battery charging state
        self.acc = 0x07e0 # accent color
        self.z1 = ( 6, # This is the "magnifying glass" shape, e.g. for the seconds hand. first line is the amount the hand sticks out *backwards* through the center
                    (0,70,0), # read: from 0% to 70% of the hand's length, offset the sides by 0 pixels
                    (70,71,1),
                    (71,72,2),
                    (72,73,3),
                    (73,75,4),
                    (75,77,4),
                    (78,79,3),
                    (79,80,2),
                    (80,81,1),
                    (81,100,0)
        )
        self.z1 = ( 6, # This is the "large magnifying glass" shape, e.g. for the seconds hand.
                    (0,100,0),
                    (100,101,1),
                    (101,102,4),
                    (102,103,6),
                    (103,104,7),
                    (104,106,8),
                    (106,107,8),                    
                    (107,108,8),
                    (108,110,7)                                        
        )
        self.z2 = (6, # This is the "rolling pin" shape, e.g. for the seconds hand.
                    (0,15,0),
                    (15,18,2),
                    (15, 18, 3),
                    (18, 21, 4),
                    (21, 79, 5),
                    (68, 69, 0, self.acc, 3), # WIP: apply different colors within a hand
                    (58, 59, 0, self.acc, 3),                    
                    (79, 82, 4),
                    (82, 85, 3),
                    (82, 85, 2),
                    (85,100,0))
        
        
    def foreground(self, effect=None):
        self.ons = ( -1, -1, -1, -1, -1, -1, -1, -1 ) # onset
        self.draw(effect)
#        wasp.system.request_event(wasp.Event.TOUCH | wasp.Event.SWIPE_UPDOWN) # if an interactive watchface, this would go here
        wasp.system.request_tick(1000)

    def tick(self, ticks):
        self.update()

    def background(self):
        pass

    def sleep(self):
        return True

    def wake(self):
        pass

    def mark(self, z, c, v, i, q, o, w, a, b): # for filesize reaons, the var names are one-letter
        # z = center (relevant if drawing secondary clock circles on the chronograph face, standard case is 120,120)
        # c = marking color
        # v = intervals of the marking
        # i = inner (starting) position, pixels from center
        # q = drawing resolution between i and o
        # o = outer (ending) position, pixels from center)
        # w = each mark's width
        # a = position in the circle to start the marking from
        # b = position in the circle to end the marking
        
        "Bezel marks"

        
        d = wasp.watch.drawable        
        for m in range(10*a,10*b,int(v*10)):
            n = math.radians(6/100*m-90)
            co = math.cos(n)
            si = math.sin(n)
            for p in range(i,o,q):
                d.fill(c, int(z[0]+co*p-w//2), int(z[1]+si*p-w//2), int(w), int(w))

    def hand(self, m, t, cy, c, l, w, r, s, prev): # for filesize reaons, the var names are one-letter
        "Draw clock hands"
        # m = ("middle") the center, relevant if drawing secondary clock circles on the chronograph face. standard is 120,120
        # t = the time
        # cy = cypher (of the digital timestamp) to draw; 0 is hours, 1 is minutes, 2 is seconds
        # c = the hand's color
        # l = the hand's length
        # w = the hand's width
        # r = drawing resolution. (Speaking for the PineTime, the seconds hand can *not* be drawn with 1 pixel resolution in less than 1 second.)
        # s = the hand's shape, one of the "z" constants in the beginning of this file
        # prev = boolean if there is an instance of this hand already on the screen (therefore has to be "undrawn" first)
        
        d = wasp.watch.drawable
        if cy == 0: # an hour hand
            an = 30*(t[3]+t[4]/60)
        else: # a minute or seconds hand
            an = 6*t[3+cy]
        o = math.cos(math.radians(an))
        i = math.sin(math.radians(an))                    
        ue = int(s[0]/100*l) # calculate actual pixel amout the hand "sticks out" backwards through the center
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
                
    def ringM(self): # The rings are secondary clock circles on the chronograph face, this one is the main clock ring.
        "Draw the main clock"
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
        "Draw a secondary small clock near the main clock's 9-hour digit"
        now = wasp.watch.rtc.get_localtime()
        draw = wasp.watch.drawable
        self.mark((55,120), gry, 1, 35, 1, 36, 1, 0, 600)
        self.mark((55,120), gry, 85.7, 17, 1, 27, 1, -43, 557)#
        self.hand((55,120), (0,0,0,0, now[6]/7*60,0), 1, clr, 36, 1, 1, self.z2, True)
        self.ons = now        
        
    def ring6(self):
        "Draw a secondary small clock near the main clock's 6-hour digit"
        now = wasp.watch.rtc.get_localtime()
        draw = wasp.watch.drawable
        self.mark((100,175), gry, 1, 30, 1, 31, 1, 0, 600)
        self.mark((100,175), gry, 85.7, 13, 1, 22, 1, -43, 557)#
        self.hand((100,175), (0,0,0,0, now[6]/7*60,0), 1, clr, 29, 1, 2, self.z1, True)
        self.ons = now        

    def ring12(self):
        "Draw a secondary small clock near the main clock's 12-hour digit"        
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

                # Since we don't have any "drawing layers", redraw parts of the screen when the main clock's hands pass (thus destroy) them (draw as soon as they have left).
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
        

        # battery indicator refresh would go here
        self.ons = now
        return True
