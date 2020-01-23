# Simple alternating logo demo

import pinetime, logo, time

def run():
    colors = (
            0xffff,
            0xf800, # red
            0xffff,
            0xffe0, # yellow
            0xffff,
            0x07e0, # green
            0xffff,
            0x07ff, # cyan
            0xffff,
            0x001f, # blue
            0xffff,
            0xf81f, # magenta
            )

    tft = pinetime.st7789()

    while True:
        for c in colors:
            tft.rleblit(logo.sx, logo.sy, logo.image, fg=c)
            time.sleep(2)

