""" Simulated ST7789 display. """

import sys
import sdl2
import sdl2.ext

CASET = 0x2a
RASET = 0x2b
RAMWR = 0x2c

class ST7789Sim(object):
    def __init__(self, width=240, height=240):
        sdl2.ext.init()

        self.width = width
        self.height = height

        self.x = 0
        self.y = 0
        self.colclip = [0, width-1]
        self.rowclip = [0, height-1]
        self.cmd = 0

        self.window = sdl2.ext.Window("ST7789", size=(width, height))
        self.window.show()
        self.windowsurface = self.window.get_surface()
        sdl2.ext.fill(self.windowsurface, (0, 0, 0))

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
            pixelview = sdl2.ext.PixelView(self.windowsurface)

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
            self.window.refresh()
