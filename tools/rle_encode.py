#!/usr/bin/env python3

# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 Daniel Thompson

import argparse
import sys
import os.path
from PIL import Image

def varname(p):
    return os.path.basename(os.path.splitext(p)[0])

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

def encode_2bit(im):
    """2-bit palette based RLE encoder.

    This encoder has a reprogrammable 2-bit palette. This allows it to encode
    arbitrary images with a full 8-bit depth but the 2-byte overhead each time
    a new colour is introduced means it is not efficient unless the image is
    carefully constructed to keep a good locality of reference for the three
    non-background colours.

    The encoding competes well with the 1-bit encoder for small monochrome
    images but once run-lengths longer than 62 start to become frequent then
    this encoding is about 30% larger than a 1-bit encoding.
    """
    pixels = im.load()
    assert(im.width <= 255)
    assert(im.height <= 255)

    rle = []
    rl = 0
    px = pixels[0, 0]
    palette = [0, 0xfc, 0x2d, 0xff]
    next_color = 1

    def encode_pixel(px, rl):
        nonlocal next_color
        px = (px[0] & 0xe0) | ((px[1] & 0xe0) >> 3) | ((px[2] & 0xc0) >> 6)
        if px not in palette:
            rle.append(next_color << 6)
            rle.append(px)
            palette[next_color] = px
            next_color += 1
            if next_color >= len(palette):
                next_color = 1
        px = palette.index(px)
        if rl >= 63:
            rle.append((px << 6) + 63)
            rl -= 63
            while rl >= 255:
                rle.append(255)
                rl -= 255
            rle.append(rl)
        else:
            rle.append((px << 6) + rl)

    # Issue the descriptor
    rle.append(2)
    rle.append(im.width)
    rle.append(im.height)

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

    return bytes(rle)

def encode_8bit(im):
    """Experimental 8-bit RLE encoder.

    For monochrome images this is about 3x less efficient than the 1-bit
    encoder. This encoder is not currently used anywhere in wasp-os and
    currently there is no decoder either (so don't assume this code
    actually works).
    """
    pixels = im.load()

    rle = []
    rl = 0
    px = pixels[0, 0]

    def encode_pixel(px, rl):
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
    print(f'static const uint8_t {varname(fname)}[] = {{')
    print(' ', end='')
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
parser.add_argument('--indent', default=0, type=int,
                    help='Add extra indentation in the generated code')
parser.add_argument('--2bit', action='store_true', dest='twobit',
                    help='Generate 2-bit image')
parser.add_argument('--8bit', action='store_true', dest='eightbit',
                    help='Generate 8-bit image')

args = parser.parse_args()
extra_indent = ' ' * args.indent
if args.eightbit:
    encoder = encode_8bit
    depth = 8
elif args.twobit:
    encoder = encode_2bit
    depth = 2
else:
    encoder = encode
    depth =1

for fname in args.files:
    image = encoder(Image.open(fname))

    if args.c:
        render_c(image, fname)
    else:
        if len(image) == 3:
            print(f'{extra_indent}# {depth}-bit RLE, generated from {fname}, '
                  f'{len(image[2])} bytes')
            (x, y, pixels) = image
            print(f'{extra_indent}{varname(fname)} = (')
            print(f'{extra_indent}    {x}, {y},')
        else:
            print(f'{extra_indent}# {depth}-bit RLE, generated from {fname}, '
                  f'{len(image)} bytes')
            pixels = image[3:]
            print(f'{extra_indent}{varname(fname)} = (')
            print(f'{extra_indent}    {image[0:1]}')
            print(f'{extra_indent}    {image[1:3]}')

        # Split the bytestring to ensure each line is short enough to
        # be absorbed on the target if needed.
        for i in range(0, len(pixels), 16):
            print(f'{extra_indent}    {pixels[i:i+16]}')
        print(f'{extra_indent})')

    if args.ascii:
        print()
        decode_to_ascii(image)
