#!/usr/bin/env python3

import argparse
import sys
from PIL import Image

def encode(im):
    pixels = im.load()

    rle = []
    rl = 0
    px = pixels[0, 0]

    def encode_pixel(px, rl):
        while rl > 255:
            rle.append(255)
            rle.append(0)
            rl -= 255
        rle.append(rl)

    for y in range(im.height):
        for x in range(im.width):
            newpx = pixels[x, y]
            if newpx == px:
                rl += 1
                assert(rl < (1 << 21))
                continue

            # Code the previous run
            encode_pixel(px, rl)

            # Start a new run
            rl = 1
            px = newpx

    # Handle the final run
    encode_pixel(px, rl)

    return (im.width, im.height, bytes(rle))

def encode_8bit(im):
    pixels = im.load()

    rle = []
    rl = 0
    px = pixels[0, 0]

    def encode_pixel(px, rl):
        print(rl)
        px = (px[0] & 0xe0) | ((px[1] & 0xe0) >> 3) | ((px[2] & 0xc0) >> 6)

        rle.append(px)
        if rl > 0:
            rle.append(px)
        rl -= 2
        if rl > (1 << 14):
            rle.append(0x80 | ((rl >> 14) & 0x7f))
        if rl > (1 <<  7):
            rle.append(0x80 | ((rl >>  7) & 0x7f))
        if rl >= 0:
            rle.append(         rl        & 0x7f )

    for y in range(im.height):
        for x in range(im.width):
            newpx = pixels[x, y]
            if newpx == px:
                rl += 1
                assert(rl < (1 << 21))
                continue

            # Code the previous run
            encode_pixel(px, rl)

            # Start a new run
            rl = 1
            px = newpx

    # Handle the final run
    encode_pixel(px, rl)

    return (im.width, im.height, bytes(rle))

def render_c(image, fname):
    print(f'// 1-bit RLE, generated from {fname}, {len(image[2])} bytes')
    print('static const uint8_t rle[] = {\n ', end='')
    i = 0
    for rl in image[2]:
        print(f' {hex(rl)},', end='')

        i += 1
        if i == 12:
            print('\n ', end='')
            i = 0

    print('\n};')

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



parser = argparse.ArgumentParser(description='RLE encoder tool.')
parser.add_argument('files', nargs='+',
                    help='files to be encoded')
parser.add_argument('--ascii', action='store_true',
                    help='Run the resulting image(s) through an ascii art decoder')
parser.add_argument('--c', action='store_true',
                    help='Render the output as C instead of python')
args = parser.parse_args()

for fname in args.files:
    image = encode(Image.open(fname))

    if args.c:
        render_c(image, fname)
    else:
        print(f'# 1-bit RLE, generated from {fname}, {len(image[2])} bytes')
        print(f'rle = {image}')

    if args.ascii:
        print()
        decode_to_ascii(image)
