# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 Daniel Thompson

# SPDX-License-Identifier: MIT
# Copyright (c) 2020 Daniel Thompson
# Copyright (c) 2016 Paul Sokolovsky

import sys
import os

class LS:
    def __repr__(self):
        self.__call__()
        return ""

    def __call__(self, path="."):
        l = os.listdir(path)
        l.sort()
        for f in l:
            st = os.stat("%s/%s" % (path, f))
            if st[0] & 0x4000:  # stat.S_IFDIR
                print("   <dir> %s" % f)
            else:
                print("% 8d %s" % (st[6], f))

class PWD:
    def __repr__(self):
        return os.getcwd()

    def __call__(self):
        return self.__repr__()

class CLEAR:
    def __repr__(self):
        return "\x1b[2J\x1b[H"

    def __call__(self):
        return self.__repr__()


pwd = PWD()
ls = LS()
clear = CLEAR()

cd = os.chdir
mkdir = os.mkdir
mv = os.rename
rm = os.remove
rmdir = os.rmdir

def head(f, n=10):
    with open(f) as f:
        for i in range(n):
            l = f.readline()
            if not l: break
            print(l, end='')

def cat(f):
    head(f, 1 << 30)

def download(path):
    head(f, 1 << 30)

def upload(path):
    print("upload mode; Ctrl-C to cancel, Ctrl-D to finish")
    with open(path, "w") as f:
        while 1:
            print('=== ', end='')
            try:
                l = input()
            except EOFError:
                break
            f.write(l)
            f.write("\n")
