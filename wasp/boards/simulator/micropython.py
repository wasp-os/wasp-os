# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 Daniel Thompson

def const(fn):
    return fn

def native(fn):
    return fn

def viper(fn):
    def ptr8(buf):
        return buf

    def ptr16(buf):
        return memoryview(buf).cast('H')

    # This is a bit of a hack since the scope for ptr8 won't be right
    # but it does mean no changes to the client
    fn.__globals__['ptr8'] = ptr8
    fn.__globals__['ptr16'] = ptr16

    return fn

