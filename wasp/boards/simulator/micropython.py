# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 Daniel Thompson

def const(fn):
    return fn

def native(fn):
    return fn

def viper(fn):
    def ptr8(buf):
        return buf

    # This is a bit of a hack since the scope for ptr8 won't be right
    # but it does mean no changes to the client
    fn.__globals__['ptr8'] = ptr8

    return fn

