# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 Daniel Thompson

class Signal(object):
    '''Simplified Signal class

    Note: The normal C implementation isn't working for the NRF port
    '''

    def __init__(self, pin, invert=False):
        self.pin = pin
        self.invert = invert

    def __call__(self, v=None):
        return self.value(v)

    def value(self, v=None):
        if v == None:
            return self.invert ^ self.pin.value()
        self.pin.value(self.invert ^ bool(v))

    def on(self):
        self.value(1)

    def off(self):
        self.value(0)
