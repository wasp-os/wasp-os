# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 Daniel Thompson

import fonts.sans18 as sans18
import fonts.sans24 as sans24
import fonts.sans28 as sans28
import fonts.sans36 as sans36

# sans24scale is a dynamically generated scaled version of the san24 font. 
# It is used like any other, e.g. draw.set_font(fonts.sans24scale)
# By default it scales by 2 in the x and y direction, this can be adjusted
# on-the-fly by writing small integers to draw._font.xscale and/or
# draw._font.yscale.
# The font is not enabled by default.  To enable, uncomment the line below and 
# include 'fonts/sans24scale.py' in the manifest list found in
# boards/manifest_240x240.py
#
# import fonts.sans24scale as sans24scale

def height(font):
    return font.height()

def width(font, s):
    w = 0
    for ch in s:
        (_, _, wc) = font.get_ch(ch)
        w += wc + 1

    return w


