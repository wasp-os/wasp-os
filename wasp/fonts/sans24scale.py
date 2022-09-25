# SPDX-License-Identifier: MY-LICENSE
# Copyright (C) 2022, Tony Robinson

from fonts.sans24 import *
from fonts.sans24 import _mvfont,_mvi

xscale = 2
yscale = 2

def height():
    return yscale * 24

def baseline():
    return yscale * 18

def max_width():
    return xscale * 23

def get_ch(ch):
    oc = ord(ch)
    ioff = 2 * (oc - 32 + 1) if oc >= 32 and oc <= 126 else 0
    doff = _mvi[ioff] | (_mvi[ioff+1] << 8)
    width = _mvfont[doff] | (_mvfont[doff+1] << 8) # _mvfont[doff+1] == 0
    nbyte0 = (width - 1)//8 + 1          # the initial number of bytes per line
    nbyte1 = (xscale * width - 1) // 8 + 1 # the final number of bytes per line
    nbit = 8 * nbyte0
    cmap = '{:0{}b}'.format(int.from_bytes(_mvfont[doff + 2:doff + 2 + nbyte0 * 24], 'big'), 24 * nbit).replace('1', '137a'[xscale-1])

    base  = 2 ** xscale                 # base of conversion to do xscale
    shift = 8 * nbyte1 - width * xscale # shift back to top bits
    chunk = [ (int(cmap[n:n+width], base) << shift).to_bytes(nbyte1, 'big') for n in range(0, len(cmap), nbit) ]

    return b''.join([x for x in chunk for _ in range(yscale)]), yscale * 24, xscale * width
