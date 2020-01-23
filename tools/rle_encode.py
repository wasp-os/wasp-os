#!/usr/bin/env python3

import sys
from PIL import Image

def encode(im):
    pixels = im.load()

    rle = []
    rl = 0
    px = 0

    for y in range(im.height):
        for x in range(im.width):
            newpx = pixels[x, y]
            if newpx == px:
                if rl < 255:
                    rl += 1
                else:
                    # Handle overflow
                    rle.append(255)
                    rle.append(0)
                    rl = 1
                continue

            # Start a new run
            rle.append(rl)
            rl = 1
            px = newpx
    # Handle the final run
    rle.append(rl)

    return (im.width, im.height, bytes(rle))

def decode_to_ascii(image):
    (sx, sy, rle) = image
    data = bytearray(2*sx)
    dp = 0
    black = ord('#')
    white = ord(' ')
    color = black

    for rl in rle:
        while rl:
            data[dp] = color
            data[dp+1] = color
            dp += 2
            rl -= 1

            if dp >= (2*sx):
                print(data.decode('utf-8'))
                dp = 0

        if color == black:
            color = white
        else:
            color = black

    # Check the image is the correct length
    assert(dp == 0)

image = encode(Image.open(sys.argv[1]))
# This is kinda cool for testing but let's leave this disabled until we add
# proper argument processing!
#decode_to_ascii(image)
print(f'# 1-bit RLE, generated from {sys.argv[1]}')
print(image)
