# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 Johannes Wache

"""
Snake Game
~~~~~~~~~~

This is a classic arcade game called snake. You have to direct the white snake to the food block (blue dot) by swiping in the desired direction. You must not hit the border or the snake's body itself.
Every time the snake eats the food, its length increases by 1. (In the current version there is an error that the length of the snake is not increased by 1 when the snake gets the food for the first time. This has to be fixed).

Once the game is over, you can try again by tapping on the screen and then swipe in the direction you want to move. If you want to leave the game, simply wipe in any direction once the game is over.

And now: Have fun playing! :)
"""

# 2-bit RLE, generated from res/snake_icon.png, 856 bytes
snake_game = (
    b'\x02'
    b'`.'
    b'\x19\x01\x16\x01?\n\x01@\x02AAQA\x80\x01\x81'
    b'\x14\x015\x81\xc0\x07\xc1@\x03R\xc1\x80\x02\x81\x01\xc0'
    b'$\xc1@IA\xceA\xc1\x016\x80\x01\x81\xc0\x03\xc1'
    b'\xc1\xd1\xc1@\x02A\x01\x80\xff\x81\x81\x8e\x81\x81\xc0$'
    b'\xc16@\x01A\x80\x03\x81\x81\x91\x81\xc0\x02\xc1\x01@'
    b'\xffAQ\x80$\x816\xc0\x01\xc1@\x03AAQA'
    b'\x80\x02\x81\x01\xc0\xdf\xc1@\xffANAA\x80$\x81'
    b'6\xc0\x01\xc1@\x03AAQA\x80\x02\x81\x01\xc0\xdf'
    b'\xc1@\xffANAA\x80$\x816\xc0\x01\xc1@\x03'
    b'AAQA\x80\x02\x81\x01\xc0\xdf\xc1@\xffANA'
    b'A\x80$\x816\xc0\x01\xc1@\x03AAQA\x80\x02'
    b'\x81\x01\xc0\xdf\xc1@\xffANAA\x80$\x816\xc0'
    b'\x01\xc1@\x03AAQA\x80\x02\x81\x01\xc0\xdf\xc1@'
    b'\xffANAA\x80$\x816\xc0\x01\xc1@\x03AA'
    b'QA\x80\x02\x81\x01\xc0\xdf\xc1@\xffANAA\x80'
    b'$\x816\xc0\x01\xc1@\x03AAQA\x80\x02\x81\x01'
    b'\xc0\xdf\xc1@\xffANAA\x80$\x816\xc0\x01\xc1'
    b'@\x03AAQA\x80\x02\x81\x01\xc0\xdf\xc1@\xffA'
    b'NAA\x80$\x816\xc0\x01\xc1@\x03AAQA'
    b'\x80\x02\x81\x01\xc0\xdf\xc1@\xffANAA\x80$\x81'
    b'6\xc0\x01\xc1@\x03AAQA\x80\x02\x81\x01\xc0\xdf'
    b'\xc1@\xffANAA\x80$\x816\xc0\x01\xc1@\x03'
    b'AAQA\x80\x02\x81\x01\xc0\xdf\xc1@\xffANA'
    b'A\x80$\x816\xc0\x01\xc1@\x03AAQA\x80\x02'
    b'\x81\x01\xc0\xdf\xc1@\xffANAA\x80$\x816\xc0'
    b'\x01\xc1@\x03AAQA\x80\x02\x81\x01\xc0\xdf\xc1@'
    b'\xffANAA\x80$\x816\xc0\x01\xc1@\x03AA'
    b'QA\x80\x02\x81\x01\xc0\xdf\xc1@\xffANAA\x80'
    b'$\x816\xc0\x01\xc1@\x03AAQA\x80\x02\x81\x01'
    b'\xc0\xff\xc1\xd1@IA6\x80\x01\x81\xc0\x03\xc1\xc1\xd1'
    b'\xc1@\x02A\x01\x80\xb6\x81\xc0\xdb\xc1\xce\xc1\xc1@$'
    b'A6\x80\x01\x81\xc0\x03\xc1\xd2\xc1@\x02A\x01\x01\x01'
    b'\x0e\x01\x01\x016\x01\x81\x81\x01\x0e\x01\x01\x81\x01\x14\x01'
    b'4\x01\x01\x01\x80H\x81\xc0I\xc1\x8e\xc1\x81\x01\x01\x01'
    b'\xc1\xc1\xce\xc1\xc1\x017\x01@\xffAQ\x80$\x81\x01'
    b'\x01AQ\x817\x01AANAA\x81\x01\x01AA'
    b'NAA\x817\x01\xc0\xdf\xc1ANAA\x81\x01\x01'
    b'\xc1ANAA\x817\x01\xc1ANAA\x81\x01\x01'
    b'\xc1ANAA\x817\x01\xc1ANAA\x81\x01\x01'
    b'\xc1ANAA\x817\x01\xc1ANAA\x81\x01\x01'
    b'\xc1ANAA\x817\x01\xc1ANAA\x81\x01\x01'
    b'\xc1ANAA\x817\x01\xc1ANAA\x81\x01\x01'
    b'\xc1ANAA\x817\x01\xc1ANAA\x81\x01\x01'
    b'\xc1ANAA\x817\x01\xc1ANAA\x81\x01\x01'
    b'\xc1ANAA\x817\x01\xc1ANAA\x81\x01\x01'
    b'\xc1ANAA\x817\x01\xc1ANAA\x81\x01\x01'
    b'\xc1ANAA\x817\x01\xc1ANAA\x81\x01\x01'
    b'\xc1ANAA\x817\x01\xc1ANAA\x81\x01\x01'
    b'\xc1ANAA\x817\x01\xc1ANAA\x81\x01\x01'
    b'\xc1ANAA\x817\x01\xc1ANAA\x81\x01\x01'
    b'\xc1ANAA\x817\x01AQ@IA\x01\x01\x80'
    b'\xff\x81\x91A7\x01\xc0\xb6\xc1@\xdbANAA\x80'
    b'$\x81\x01\x01\xc1ANAA\x818\x12\x03\x12?\r'
    b'\x01\x14\x01?\x9c'
)


import wasp, time
from random import randint

class SnakeGameApp():
    NAME = 'Snake'
    ICON = snake_game

    def __init__(self):
        self.running = True
        self.snake = Snake()
        self.food_location()
        self.highscore = 1


    def foreground(self):
        """Activate the application."""
        wasp.watch.drawable.fill()
        if self.running:
            self.update()
        else: 
            self.snake.show()
            wasp.watch.drawable.fill(x=self.food[0],y=self.food[1],w=15,h=15,bg=0x00ff)
        wasp.system.request_event(wasp.EventMask.TOUCH |
                                  wasp.EventMask.SWIPE_UPDOWN |
                                  wasp.EventMask.SWIPE_LEFTRIGHT)
        wasp.system.request_tick(250)

    def touch(self,event):
        if not self.running:
            self.running = True
            wasp.watch.drawable.fill()

    def swipe(self, event):
      if self.running:
        """Notify the application of a touchscreen swipe event."""
        if event[0] == wasp.EventType.UP:
            self.snake.set_dir(0,-15)
        elif event[0] == wasp.EventType.DOWN:
            self.snake.set_dir(0,15)
        elif event[0] == wasp.EventType.LEFT:
            self.snake.set_dir(-15,0)
        elif event[0] == wasp.EventType.RIGHT:
            self.snake.set_dir(15,0)
      else:
        return True

    def tick(self, ticks):
        """Notify the application that its periodic tick is due."""
        self.update()

    def food_location(self):
        x = randint(0,15) * 15
        y = randint(0,15) * 15
        self.food = [x,y]

    def update(self):
        draw = wasp.watch.drawable
        """Draw the display from scratch."""

        if (self.snake.eat(self.food)):
            self.food_location()
        self.snake.update()
        if (self.snake.end_game()):
                if len(self.snake.body) > self.highscore:
                    self.highscore = len(self.snake.body)
                self.running = False
                wasp.watch.vibrator.pulse()
                self.snake = Snake()
                draw.fill()
                draw.set_color(0xf000)
                draw.string('GAME', 0, 60, width=240)
                draw.string('OVER', 0, 98, width=240)
                draw.string('Highscore: '+str(self.highscore-1),0,180,width=240)
                draw.reset()
                return True
        if self.running:
            self.snake.show()
            draw.fill(x=self.food[0],y=self.food[1],w=15,h=15,bg=0x00ff)
        return True


# Based on https://www.youtube.com/watch?v=OMoVcohRgZA
class Snake():
    def __init__(self):
        self.body = [[120,120]]
        self.xdir = 0
        self.ydir = 0
        self.justate = False
        self.oldtail = [0,0]

    def set_dir(self,x,y):
        self.xdir = x
        self.ydir = y

    def update(self):     
        self.oldtail = self.body[0].copy()
        head = self.body[-1].copy()
        if not self.justate: 
            self.body = self.body[1:]
        self.justate = False
        head[0] += self.xdir
        head[1] += self.ydir
        self.body.append(head)

    def eat(self,pos):
        x = self.body[-1][0]
        y = self.body[-1][1]
        if (x == pos[0] and y == pos[1]):
            self.justate = True
            # Color food white so it appears as a body part:
            wasp.watch.drawable.fill(x=(self.body[-1][0]),y=(self.body[-1][1]),w=15,h=15,bg=0x0000)
            wasp.watch.drawable.fill(x=self.body[-1][0]+1,y=self.body[-1][1]+1,w=13,h=13,bg=0xffff)
            return True
        return False

    def end_game(self):
        x = self.body[-1][0]
        y = self.body[-1][1]
        if (x >= 240 or x < 0) or (y >= 240 or y < 0):
            return True
        for i in range(len(self.body)-1):
            part = self.body[i]
            if (part[0] == x and part[1] == y):
                return True
        return False

    def show(self):
        draw = wasp.watch.drawable
        draw.fill(x=self.oldtail[0],y=self.oldtail[1],w=15,h=15,bg=0x0000)
        draw.fill(x=self.body[-1][0]+1,y=self.body[-1][1]+1,w=13,h=13,bg=0xffff)

        # if(self.justate):
        #     self.justate = False
        #     if len(self.body) == 1 or len(self.body) == 2:
        #         # Here is movement after eating for a snake of size one
        #         print("case 1")
        #         print(self.body[-1][0])
        #         print(self.body[-1][1])
        #         draw.fill(x=self.body[-1][0],y=self.body[-1][1],w=13,h=13,bg=0xffff)
        #     else:
        #         # Here is movement after eating for a snake of size more than one
        #         print("case 2")
        #         draw.fill(x=self.body[-1][0],y=self.body[-1][1],w=13,h=13,bg=0xffff)
        # else:
        #     if len(self.body) == 1:
        #         # Here is normal movement for a snake of size one
        #         print("case 3")
        #         print("erease old tail:")
        #         print(self.body[0][0]-self.xdir)
        #         print(self.body[0][1]-self.ydir)
        #         print("draw new head")
        #         print(self.body[0][0]+1)
        #         print(self.body[0][1]+1)
        #         draw.fill(x=(self.body[0][0]-self.xdir),y=(self.body[0][1]-self.ydir),w=15,h=15,bg=0x0000)
        #         draw.fill(x=self.body[0][0]+1,y=self.body[0][1]+1,w=13,h=13,bg=0xffff)
        #     else:
        #         # Here is normal movement for a snake of size more than one
        #         print("case 4")
        #         print("erease old tail:")
        #         print(self.body[0][0])
        #         print(self.body[0][1])
        #         print("draw new head")
        #         print(self.body[-1][0])
        #         print(self.body[-1][1])
        #         # draw.fill(x=self.body[0][0],y=self.body[0][1],w=15,h=15,bg=0x0000)
        #         draw.fill(x=self.oldtail[0],y=self.oldtail[1],w=15,h=15,bg=0x0000)
        #         draw.fill(x=self.body[-1][0],y=self.body[-1][1],w=13,h=13,bg=0xffff)
