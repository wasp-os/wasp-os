#
# Logo demo for PineTime
#
# This demo is simply an alternating sweep of the Pine64 and
# MicroPython logos. It cycles through a variety of colours
# and swaps between the logos every 5 images (so make sure
# len(colors) is not a multiple of 5 ;-) ).
#

import watch, logo, time, gc

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

def run():
    l = logo.pine64
    i = 0

    watch.display.poweron()
    watch.backlight.set(2)

    while True:
        for c in colors:
            if i < 5:
                i += 1
            else:
                i = 0
                if l == logo.pine64:
                    l = logo.micropython
                else:
                    l = logo.pine64
                watch.display.fill(0)

            watch.display.rleblit(l, fg=c)
            time.sleep(2)
            gc.collect()
