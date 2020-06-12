# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 Daniel Thompson

import time
def sleep_ms(ms):
    time.sleep(ms / 1000)
time.sleep_ms = sleep_ms

import sys, traceback
def print_exception(exc, file=sys.stdout):
    exc_type, exc_value, exc_traceback = sys.exc_info()
    traceback.print_exception(exc_type, exc_value, exc_traceback, file=file)
sys.print_exception = print_exception

import draw565
import array

from machine import I2C
from machine import Pin
from machine import SPI

from drivers.cst816s import CST816S
from drivers.st7789 import ST7789_SPI
from drivers.vibrator import Vibrator

class Accelerometer:
    """Simulated accelerometer.

    Accelerometers such as BMA421 are complex and most of the driver
    is written in C. For that reason we simulate the accelerometer
    rather than emulate (by comparison we emulate the ST7789).
    """
    def reset(self):
        self._steps = 3

    @property
    def steps(self):
        """Report the number of steps counted."""
        if self._steps < 10000:
            self._steps = int(self._steps * 1.34)
        else:
            self._steps += 1
        return self._steps

    @steps.setter
    def steps(self, value):
        self.reset()

class Backlight(object):
    def __init__(self, level=1):
        pass

    def set(self, level):
        """Set the simulated backlight level.

        This function contains a subtle trick. As soon as the backlight is
        turned off (e.g. the watch goes to sleep) then we will simulate
        a button press in order to turn the watch back on again.
        """
        print(f'BACKLIGHT: {level}')

        button.value(bool(level))

class Battery(object):
    def __init__(self):
        self.voltage = 3.9
        self.step = -0.01
        self.powered = False

    def charging(self):
        self.voltage_mv()
        return self.powered

    def power(self):
        self.voltage_mv()
        return self.powered

    def voltage_mv(self):
        if self.voltage > 4:
            self.step = -0.01
            self.powered = False
        elif self.voltage < 3.4:
            self.step = 0.04
            self.powered = True
        self.voltage += self.step

        return int(self.voltage * 1000)

    def level(self):
        mv = self.voltage_mv()
        level = ((19 * mv) // 100) - 660
        if level > 100:
            return 100
        if level < 0:
            return 0
        return level

class RTC(object):
    def __init__(self):
        self._epoch = time.time()
        self._lasttime = 0

    def update(self):
        now = time.time()
        if now == self._lasttime:
            return False
        self._lasttime = now
        return True

    def get_localtime(self):
        #if self.uptime < 60:
        #    # Jump back a little over a day
        #    return time.localtime(time.time() - 100000)
        return time.localtime()

    def get_time(self):
        now = self.get_localtime()
        return (now[3], now[4], now[5])

    @property
    def uptime(self):
        return time.time() - self._epoch

    def get_uptime_ms(self):
        return int(self.uptime * 1000)

backlight = Backlight()
spi = SPI(0)
spi.init(polarity=1, phase=1, baudrate=8000000)
display = ST7789_SPI(240, 240, spi,
        cs=Pin("DISP_CS", Pin.OUT, quiet=True),
        dc=Pin("DISP_DC", Pin.OUT, quiet=True),
        res=Pin("DISP_RST", Pin.OUT, quiet=True))
drawable = draw565.Draw565(display)

accel = Accelerometer()
battery = Battery()
button = Pin('BUTTON', Pin.IN, quiet=True)
rtc = RTC()
touch = CST816S(I2C(0), Pin('TP_INT', Pin.IN, quiet=True), Pin('TP_RST', Pin.OUT, quiet=True))
vibrator = Vibrator(Pin('MOTOR', Pin.OUT, value=0), active_low=True)

