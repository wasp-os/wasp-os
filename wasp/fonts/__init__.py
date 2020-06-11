# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 Daniel Thompson

import fonts.sans24 as sans24
import fonts.sans28 as sans28
import fonts.sans36 as sans36

def height(font):
    return font.height()

def width(font, s):
    w = 0
    for ch in s:
        (_, _, wc) = font.get_ch(ch)
        w += wc + 1

    return w


