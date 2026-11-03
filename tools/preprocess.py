#!/usr/bin/env python3

# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 Daniel Thompson
"""Quick and dirty macro processor.

Supported macros:

 * ``#include('file')`` -- splice in another file
 * ``#build_time('NAME')`` -- emit ``NAME = (yyyy, mm, dd, HH, MM, SS, 0, 0)``
   for the time of the build (or SOURCE_DATE_EPOCH if set, so that
   reproducible builds stay reproducible)
"""

import os
import sys
import time

def preprocess(fname):
    with open(fname) as f:
        for ln in f.readlines():
            ln = ln.rstrip()

            macro = ln.lstrip()
            if macro.startswith('#include') or macro.startswith('#build_time'):
                exec(macro[1:])
            else:
                print(ln)

def include(fname):
    preprocess(fname)

def build_time(name):
    epoch = int(os.environ.get('SOURCE_DATE_EPOCH', time.time()))
    # never earlier than the historical default of 2020-03-01
    t = time.localtime(max(epoch, 1583020800))
    print('%s = (%d, %d, %d, %d, %d, %d, 0, 0)' % ((name,) + tuple(t[:6])))

for arg in sys.argv[1:]:
    preprocess(arg)
