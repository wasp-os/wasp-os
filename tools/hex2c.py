#!/usr/bin/env python3

# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 Daniel Thompson

import binascii
import intelhex
import sys

def generate_c(ihex):
    print('/* this file is auto-generated - DO NOT EDIT */')
    print()
    print('#include <stdint.h>')
    print()
    print('struct segment {')
    print('    uint32_t start;');
    print('    uint32_t end;');
    print('    uint32_t crc32;')
    print('    const uint8_t *data;')
    print('};')
    print()

    for i, segment in enumerate(ihex.segments()):
        print(f'static const uint8_t segment{i}[] = {{', end='')

        for j in range(segment[0], segment[1]):
            if 0 == j % 12:
                print('\n   ', end='')
            print(f' 0x{ihex[j]:02x},', end='')

        print('\n};\n')
    print(f'const struct segment segments[] = {{')
    for i, segment in enumerate(ihex.segments()):
        sg = ihex.tobinarray(start=segment[0], end=segment[1]-1)
        crc = binascii.crc32(sg)
        print(f'    0x{segment[0]:08x}, 0x{segment[1]:08x}, 0x{crc:08x}, segment{i},')
    print('};')

ihex = intelhex.IntelHex()
ihex.loadhex(sys.argv[1])
generate_c(ihex)
