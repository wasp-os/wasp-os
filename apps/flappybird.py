# SPDX-License-Identifier: CC0
# Copyright (C) YEAR(2023), Tigercoding56
from micropython import const
import wasp
import drivers 
import micropython
import machine
import time



class FlappybirdApp():
    NAME = "Flappy"
    ICON= (
        b'\x02`@-@\tL?\x10E\x80,\x8cE?\tB\x96B?\x04C\x87L\x87C>B\x86D\xc0-\xccD\x86B;A\x85C\xd4C\x85A8B\x84B\xdaB\x84B5A\x84B\xc9@\xd7L\xc9\x80\t\x82\xc0,\xc4\x813\x81\xc4\x81@-G\x80\xd7\x94G\xc0\t\xc1@,D\xc11\xc1C\xc2\x80-\x85\xc0\xd7\xda\x85@\tB\x80,\x83A/A\x83A\xc0-\xc5@\xd7J\x80\x1d\x8bI\xc5\xc0\t\xc1@,C\xc1-\xc1C\xc1\x80-\x84\xc0\xd7\xc9@\x1dQ\xc8\x84\x80\t\x81\xc0,\xc3\x81+\x81\xc3\x81@-D\x80\xd7\x87\xc0\x1d\xd7\x86D@\tA\x80,\x83A)A\x83A\xc0-\xc4@\xd7G\x80\x1d\x99F\xc4\xc0\t\xc1@,C\xc1\'\xc1C\xc1\x80-\x84\xc0\xd7\xc6@\x1d]\xc5\x84\x80\t\x81\xc0,\xc3\x81&\x81\xc2\x81@-C\x80\xd7\x87\xc0\x1d\xdf\x86C@\tA\x80,\x82A%A\x83A\xc0-\xc3@\xd7E\x80\x1d\xa3D\xc3\xc0\t\xc1@,C\xc1$\xc1B\xc1\x80-\x83\xc0\xd7\xc5@\x1de\xc4\x83\x80\t\x81\xc0,\xc2\x81#\x81\xc2\x81@-C\x80\xd7\x85\xc0\x1d\xe7\x84C@\tA\x80,\x82A"A\x82A\xc0-\xc2@\xd7F\x80\x1d\xa7E\xc2\xc0\t\xc1@,B\xc1!\xc1B\xc1\x80-\x83\xc0\xd7\xc5@\x1dh\x01\xc4\x83\x80\t\x81\xc0,\xc2\x81 \x81\xc2\x81@-B\x80\xd7\x85\x01\xc0\x1d\xe8\x02\x84B@\tA\x80,\x82A\x1fA\x83A\xc0-\xc2@\xd7D\x02\x80\x1d\xa8\x02D\xc2\xc0\t\xc1@,C\xc1\x1e\xc1B\xc1\x80-\x82\xc0\xd7\xc5\x02@\x1dh\x03\xc4\x82\x80\t\x81\xc0,\xc2\x81\x1e\x81\xc2\x81@-B\x80\xd7\x85\x02\xc0\x1d\xe8\x03\x84B@\tA\x80,\x82A\x1eA\x82A\xc0-\xc2@\xd7D\x03\x80\x1d\xa8\x04C\xc2\xc0\t\xc1@,B\xc1\x1d\xc1B\xc1\x80-\x83\xc0\xd7\xc4\x03@\x1dh\x04\xc3\x83\x80\t\x81\xc0,\xc2\x81\x1c\x81\xc2\x81@-B\x80\xd7\x85\x03\xc0\x1d\xe8\x04\x84B@\tA\x80,\x82A\x1cA\x82A\xc0-\xc2@\xd7D\x04\x80\x1d\xa8\x05C\xc2\xc0\t\xc1@,B\xc1\x1c\xc1B\xc1\x80-\x82\xc0\xd7\xc4\x04@\x1dh\x05\xc3\x82\x80\t\x81\xc0,\xc2\x81\x1c\x81\xc2\x81@-B\x80\xd7\x84\x04\xc0\x1d\xe8\x05\x83B@\tA\x80,\x82A\x1cA\x82A\xc0-\xc2@\xd7D\x04\x80\x1d\xa8\x05C\xc2\xc0\t\xc1@,B\xc1\x1c\xc1B\xc1\x80-\x82\xc0\xd7\xc4\x04@\x1dh\x05\xc3\x82\x80\t\x81\xc0,\xc2\x81\x1c\x81\xc2\x81@-B\x80\xd7\x84\x04\xc0\x1d\xe8\x05\x83B@\tA\x80,\x82A\x1cA\x82A\xc0-\xc2@\xd7D\x04\x80\x1d\xa8\x05C\xc2\xc0\t\xc1@,B\xc1\x1c\xc1B\xc1\x80-\x82\xc0\xd7\xc4\x04@\x1dE\x80a\x85^\x05\xc3\xc0-\xc2@\tA\x80,\x82A\x1cA\x82A\xc2\xc0\xd7\xc4\x04@\x1dF\x80a\x81\x81\x81_\x05\xc3\xc0-\xc2@\tA\x80,\x82A\x1cA\x82A\xc3\xc0\xd7\xc4\x03@\x1dF\x80a\x81\x81\x81L\x85N\x04\xc3\xc0-\xc3@\tA\x80,\x82A\x1dA\x82A\xc2\xc0\xd7\xc4\x03@\x1dF\x80a\x81\x81\x81M\x81\x81\x81O\x04\xc3\xc0-\xc2@\tA\x80,\x82A\x1eA\x82A\xc2\xc0\xd7\xc4\x03@\x1dF\x80a\x81\x81\x81M\x81\x81\x81O\x04\xc3\xc0-\xc2@\tA\x80,\x82A\x1eA\x82A\xc2\xc0\xd7\xc5\x02@\x1dF\x80a\x81\x81\x81M\x81\x81\x81O\x03\xc4\xc0-\xc2@\tA\x80,\x82A\x1eA\x83A\xc2\xc0\xd7\xc4\x02@\x1dF\x80a\x81\x81\x81M\x81\x81\x81O\x03\xc3\xc0-\xc2@\tA\x80,\x83A\x1fA\x82A\xc2\xc0\xd7\xc5\x01@\x1dF\x80a\x81\x81\x81M\x81\x81\x81O\x02\xc4\xc0-\xc2@\tA\x80,\x82A A\x82A\xc3\xc0\xd7\xc4\x01@\x1dF\x80a\x81\x81\x81M\x81\x81\x81D\x85F\x02\xc3\xc0-\xc3@\tA\x80,\x82A!A\x82A\xc2\xc0\xd7\xc4\x01@\x1dF\x80a\x81\x81\x81B\x85F\x81\x81\x81E\x81\x81\x81G\x01\xc4\xc0-\xc2@\tA\x80,\x82A"A\x82A\xc3\xc0\xd7\xc5@\x1dE\x80a\x81\x81\x81C\x81\x81\x81G\x81\x81\x81E\x81\x81\x81G\xc4\xc0-\xc3@\tA\x80,\x82A#A\x82A\xc3\xc0\xd7\xc4@\x1dE\x80a\x81\x81\x81C\x81\x81\x81G\x81\x81\x81E\x81\x81\x81G\xc3\xc0-\xc3@\tA\x80,\x82A$A\x83A\xc3\xc0\xd7\xc4@\x1dD\x80a\x81\x81\x81C\x81\x81\x81G\x81\x81\x81E\x81\x81\x81F\xc3\xc0-\xc3@\tA\x80,\x83A%A\x82A\xc3\xc0\xd7\xc5@\x1dC\x80a\x81\x81\x81C\x81\x81\x81G\x81\x81\x81E\x81\x81\x81E\xc4\xc0-\xc3@\tA\x80,\x82A&A\x83A\xc4\xc0\xd7\xc5@\xa9A\x80a\x81\x81\x81C\x81\x81\x81G\x81\x81\x81E\x81\x81\x81C\xc4\xc0-\xc4@\tA\x80,\x83A\'A\x83A\xc4\xc0\xd7\xc5@\xa9A\x80\xd4\x82A\x82A\x85A\x84A\x84A\x86\xc4\xc0-\xc4@\tA\x80,\x83A)A\x83A\xc4\xc0\xd7\xc6@\xd4B\x80\xa9\x81B\x81E\x81D\x81D\x81C\xc5\xc0-\xc4@\tA\x80,\x83A+A\x83A\xc4\xc0\xd7\xc6@\xd4B\x80\xa9\x81B\x81E\x81D\x81D\x81A\xc5\xc0-\xc4@\tA\x80,\x83A-A\x83A\xc5\xc0\xd7\xc7@\xd4C\x80\xa9\x81E\x81D\x81B\xc6\xc0-\xc5@\tA\x80,\x83A/A\x83B\xc5\xc0\xd7\xc8@\xd4A\x80\xa9\x81E\x81C\xc7\xc0-\xc5@\tB\x80,\x83A1A\x84A\xc7\xc0\xd7\xd4@-G\x80\t\x81\xc0,\xc4\x813\x81\xc4\x82I@\xd7L\x80-\x89\xc0\t\xc2@,D\xc15\xc2D\xc2\x9a\xc2D\xc28\xc1E\xc3\x94\xc3E\xc1;\xc2F\xc4\x8c\xc4F\xc2>\xc3G\xccG\xc3?\x04\xc2V\xc2?\t\xc5L\xc5?\x10\xcc\''
        )
    def tick(self,ticks):
        self.ttime = (self.ttime + 1) % 20
        self._draw()
        
    def ssp(self,image,x,y):
            self.draw.blit(image,x,y)

    def __init__(self):
        self.playerx = 120
        self.playery = 140
        self.oly = self.playery
        self.velocity = -10
        self.maxheight =240
        self.maxlenght = 240
        self.input = 0
        self.time = 0
        self.ttime =0
        self.score = 0
        self.bars = const([40,20,60,50,80,60])
        self.driver = wasp.watch.display
        self.draw = wasp.watch.drawable
    def pipe(self,y,t):
        x = ((t +(0-self.playerx)) % 300)
        xt = (((t+5) +(0-self.playerx)) % 300)
        if not (x > 230 or x < 10):
                self.draw.fill(x=x-5,y=(230 - y),w=10,h=y,bg=0x07e0)
        if not (xt > 236 or xt < 6):
                self.draw.fill(x=xt,y=(230 - y),w=3,h=y,bg=0x001f)
        if x > 110 and x < 125:
            if self.playery < y:
                self.playerx = 0
                self.time = 0
                self.score = 0
                self.draw.fill(x=0,y=24,w=240,h=216,bg=0x001f)
                self.oly = 140
                self.playery = 140
            else:
                self.score = self.score + 0.1
    def foreground(self):
        wasp.system.request_tick(20)
        wasp.system.request_event(wasp.EventMask.TOUCH)
        self.draw.fill(x=0,y=24,w=240,h=216,bg=0x001f)
        self._draw()
        time = 0
        playerx = 0
    def gamelogic(self):
        self.playery += self.velocity
        self.velocity = self.velocity - 1
        if self.playery < 10:
            self.playery = 10
        elif self.playery > 140:
            self.playery = 140
        if self.velocity > 20:
            self.velocity = 20
        if self.velocity < -10:
            self.velocity = -10
    def _draw(self):
        self.gamelogic()
        self.playerx = (self.playerx + 2)% 300
        self.driver.quick_start()
        self.draw.fill(x=110,y=(230 - self.oly),w=10,h=10,bg=0x001f)
        self.draw.fill(x=110,y=(230 - self.playery),w=10,h=10,bg=0xfea8)
        self.oly = self.playery
        for i in range(0,5):
            self.pipe(self.bars[i], i * 50)
        self.draw.string("score:" +str(int(self.score)), 0, 0, width=240)
        self.driver.quick_end()
    def touch(self, event):
            if self.velocity < 0:
                self.velocity = self.velocity + 5
            else:
                self.velocity = self.velocity + 1
        




        
