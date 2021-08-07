#!/usr/bin/env python3

# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2021 Daniel Thompson

import sys

def parse_record(view):
    '''Consume a single set of samples and format as a line for a CSV file.'''
    # Verify synchronization
    assert(view[0] == 0xffff)

    # Extract the timestamp and format it in ISO 8601 format
    (YY, MM, DD, hh, mm, ss) = view[1:7]
    print(f'"{YY:04}{MM:02}{DD:02}T{hh:02}{mm:02}{ss:02}"', end='')

    # Consume data until we reach the synchronization token
    offset = 8
    while offset < len(view) and view[offset] != 0xffff:
        print(f',{view[offset]}', end='')
        offset += 1

    # Close the current record and return
    print('')
    return offset

# Open and read the file named in our first argument
with open(sys.argv[1], 'rb') as f:
    rawdata = f.read()

# Re-interpret the raw data as an array of 16-bit values
view = memoryview(rawdata)
data = view.cast('H')

# Process the data one record at a time
offset = 0
while offset < len(data):
    offset += parse_record(data[offset:])
