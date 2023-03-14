# SPDX-License-Identifier: CC0
# Copyright (C) 2023 benedikt moore (did i do it right?)
"""Drawing Application
~~~~~~~~~~~~~~~~~~~~

this application allows users to draw a image
which gradually gets erased afterward

.. figure:: res/DrawApp.png
    :width: 179
"""
import wasp
import icons

class DrawApp():
    NAME = 'Draw'
    ICON = icons.app

    def __init__(self):
        self.draw = wasp.watch.drawable
        self.pnts = []
        self.cursor = [0,0]

    def foreground(self):
        self._draw()
        wasp.system.request_event(wasp.EventMask.TOUCH | wasp.EventMask.SWIPE_UPDOWN|wasp.EventMask.SWIPE_LEFTRIGHT  )
        wasp.system.request_tick(400)

    def lerp(self,x1,x2,x3):
        return (( x1 - x2 ) * x3 ) +x1
    def line(self,x1,x2):
        for i in range(1,9):
            x =self.lerp(x1[0],x2[0],((10-i) * 0.1)) + (x2[0]-x1[0])
            y = self.lerp(x1[1],x2[1],((10-i) * 0.1))  + (x2[1]-x1[1]) 
            if x > 10 and y > 10 and y < 230 and x < 230:
                self.pnts.append((x,y))
                x = int(x)
                y = int(y)
                self.draw.fill(x=x,y=y,w=10,h=10,bg=0x001f)
                print((x,y))
            else:
                print((x,y))
    def tick(self, ticks):
        for i in range(0,int(len(self.pnts)*0.02)+1):
            if len(self.pnts) > 0:
                self.draw.fill(x=int(self.pnts[0][0]),y=int(self.pnts[0][1]),w=10,h=10,bg=0x0000)
                del self.pnts[0]

                
            

    def touch(self, event):
        wasp.system.keep_awake()
        self.cursor = [event[1],event[2]]
        if event[1] > 10 and event[2] > 10 and event[1] < 230 and event[2] < 230:
            try:
                self.pnts.append((event[1],event[2]))
                self.draw.fill(x=event[1],y=event[2],w=10,h=10,bg=0x001f)
            except:
                io = 0
    def _draw(self):
        self.draw.fill()
    def swipe(self,event):

        cursor2 =  [list(event)[1],list(event)[2]]
        if cursor2[0] > 10 and cursor2[1] > 10 and cursor2[1] < 230 and cursor2[0] < 230:
                    self.line(self.cursor,cursor2)
                    self.cursor = cursor2

        return False
   


