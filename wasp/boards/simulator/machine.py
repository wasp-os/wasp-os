# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 Daniel Thompson

import display
import time

class Tracer(object):
    def __init__(self, *args, **kwargs):
        print(f'{self.__class__.__name__}.__init__{args} {kwargs}')

    def __getattr__(self, name):
        if name.upper() == name:
            return name
        return lambda *args, **kwargs: print(f'{self.__class__.__name__}.{name}{args} {kwargs}')

class ADC(Tracer):
    pass

class Pin(object):
    IN = 'IN'
    OUT = 'OUT'
    IRQ_FALLING = 'IRQ_FALLING'

    pins = {}

    def __init__(self, id, direction, value=1, quiet=False):
        self._id = id
        self._value = 0
        self._quiet = quiet

        # Update the pin registry
        self.pins[id] = self

    def irq(self, trigger, handler):
        self._handler = handler

    def init(self, d, value):
        self.value(value)

    def on(self):
        self.value(1)

    def off(self):
        self.value(0)

    def raise_irq(self):
        self._handler(self)

    def value(self, v=None):
        if v is None:
            if not self._quiet:
                print(f'{self._id}: read {self._value}')
            return self._value
        if v:
            if not self._quiet:
                print(self._id + ": set on")
            self._value = False
        else:
            if not self._quiet:
                print(self._id + ": set off")
            self._value = True

    def __call__(self, v=None):
        self.value(v)

class PWM(Tracer):
    FREQ_16MHZ = 'FREQ_16MHZ'

class SPI(object):
    def __init__(self, id):
        self._id = id
        if id == 0:
            self.sim = display.spi_st7789_sim
        else:
            self.sim = None

    def init(self, baudrate=1000000,  polarity=0, phase=0, bits=8, sck=None, mosi=None, miso=None):
        pass

    def write(self, buf):
        if self.sim:
            self.sim.write(buf)
        else:
            print("Sending data: " + str(buf))

class I2C():
    def __init__(self, id):
        self.id = id
        if id == 0:
            self.sim = display.i2c_cst816s_sim
        else:
            self.sim = None

    def readfrom_mem_into(self, addr, reg, dbuf):
        if self.sim:
            self.sim.readfrom_mem_into(addr, reg, dbuf, Pin.pins)
        else:
            raise OSError

    def writeto_mem(self, addr, reg, dbuf):
        if self.sim:
            self.sim.writeto_mem(addr, reg, dbuf, Pin.pins)
        else:
            raise OSError

class Timer():
    def __init__(self, id, period=1000000):
        self.then = None
        self.period = period

    def start(self):
        self.then = time.time()

    def stop(self):
        self.then = None

    def time(self):
        now = time.time()
        elapsed_sec = now - self.then
        elapsed_us = int(elapsed_sec * 1000000)

        return elapsed_us % self.period

    def period(self):
        self.time()

def lightsleep(ms=10):
    display.tick(Pin.pins)
    time.sleep(ms / 1000)

def deepsleep(ms=10):
    lightsleep(ms)
