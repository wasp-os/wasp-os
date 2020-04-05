# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 Daniel Thompson

""" Simulated ST7789 display and CST816S touchscreen. """

import sys
import sdl2
import sdl2.ext

CASET = 0x2a
RASET = 0x2b
RAMWR = 0x2c

WIDTH = 240
HEIGHT = 240

class ST7789Sim(object):
    def __init__(self):

        self.x = 0
        self.y = 0
        self.colclip = [0, WIDTH-1]
        self.rowclip = [0, HEIGHT-1]
        self.cmd = 0

    def write(self, data):
        if len(data) == 1:
            # Assume if we get a byte at a time then it is command.
            # This is a simplification do we don't have to track
            # the D/C pin from within the simulator.
            self.cmd = data[0]

        elif self.cmd == CASET:
            self.colclip[0] = (data[0] << 8) + data[1]
            self.colclip[1] = (data[2] << 8) + data[3]
            self.x = self.colclip[0]

        elif self.cmd == RASET:
            self.rowclip[0] = (data[0] << 8) + data[1]
            self.rowclip[1] = (data[2] << 8) + data[3]
            self.y = self.rowclip[0]

        elif self.cmd == RAMWR:
            pixelview = sdl2.ext.PixelView(windowsurface)

            half = False
            for d in data:
                if not half:
                    rgb = d << 8
                    half = True
                    continue
                rgb |= d
                half = False

                pixel = ((rgb & 0xf800) >> 8,
                         (rgb & 0x07e0) >> 3,
                         (rgb & 0x001f) << 3)
            
                pixelview[self.y][self.x] = pixel

                self.x += 1
                if self.x > self.colclip[1]:
                    self.x = self.colclip[0]
                    self.y += 1
                if self.y > self.rowclip[1]:
                    self.y = self.rowclip[0]
            
            # Forcibly release the surface to ensure it is unlocked
            del pixelview
            window.refresh()

class CST816SSim():
    def __init__(self):
        self.regs = bytearray(64)

    def readfrom_mem_into(self, addr, reg, dbuf):
        tick()

        if not self.regs[1]:
            raise OSError

        dbuf[:] = self.regs[reg:len(dbuf)+reg]
        if self.regs[3]:
            self.regs[3] = 0
        else:
            self.regs[1] = 0

    def handle_key(self, key):
        """Use key presses to provoke different touchscreen events.

        Note: The Down key provokes an upward swipe and vice versa.
              Same for left and right. That is because the swipe up
              gesture means show me the screen the is below me (hence
              the controls are inverted compared to joystick-like
              direction control).
        """
        if key.keysym.sym == sdl2.SDLK_DOWN:
            self.regs[1] = 2
        elif key.keysym.sym == sdl2.SDLK_UP:
            self.regs[1] = 1
        elif key.keysym.sym == sdl2.SDLK_LEFT:
            self.regs[1] = 4
        elif key.keysym.sym == sdl2.SDLK_RIGHT:
            self.regs[1] = 3
        self.regs[3] = 0x80
        self.raise_interrupt()

    def handle_mousebutton(self, button):
        self.regs[1] = 5
        self.regs[4] = button.x
        self.regs[6] = button.y
        self.raise_interrupt()

    def raise_interrupt(self):
        pass

sdl2.ext.init()
window = sdl2.ext.Window("ST7789", size=(WIDTH, HEIGHT))
window.show()
windowsurface = window.get_surface()
sdl2.ext.fill(windowsurface, (0, 0, 0))

spi_st7789_sim = ST7789Sim()
i2c_cst816s_sim = CST816SSim()

def tick():
    events = sdl2.ext.get_events()
    for event in events:
        if event.type == sdl2.SDL_QUIT:
            sdl2.ext.quit()
            sys.exit(0)
        elif event.type == sdl2.SDL_MOUSEBUTTONDOWN:
            i2c_cst816s_sim.handle_mousebutton(event.button)
        elif event.type == sdl2.SDL_KEYDOWN:
            i2c_cst816s_sim.handle_key(event.key)
        else:
            #print(event)
            pass
    window.refresh()
