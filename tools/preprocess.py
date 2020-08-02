#!/usr/bin/env python3

# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 Daniel Thompson
"""Quick and dirty macro processor.

Currently the only support macro is #include!
"""

import sys

def preprocess(fname):
    with open(fname) as f:
        for ln in f.readlines():
            ln = ln.rstrip()

            macro = ln.lstrip()
            if macro.startswith('#include'):
                exec(macro[1:])
            else:
                print(ln)

def include(fname):
    preprocess(fname)

for arg in sys.argv[1:]:
    preprocess(arg)
