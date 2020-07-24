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

class HRS():
    DATA = (
9084,9084,9025,9025,9009,9009,9009,9015,9015,9024,9024,9024,9073,9073,9074,9074,
9074,9100,9100,9097,9097,9097,9045,9045,9023,9023,9023,9035,9035,9039,9039,9039,
9049,9049,9052,9052,9052,9066,9066,9070,9070,9070,9078,9078,9081,9081,9081,9092,
9092,9093,9093,9093,9094,9094,9108,9108,9108,9124,9124,9122,9122,9122,9100,9100,
9110,9110,9110,9112,9112,9118,9118,9118,9127,9127,9136,9136,9136,9147,9147,9154,
9154,9154,9156,9156,9153,9153,9153,9152,9152,9156,9156,9156,9161,9161,9161,9177,
9177,9186,9186,9196,9196,9196,9201,9201,9201,9189,9189,9176,9176,9176,9176,9176,
9175,9175,9175,9175,9175,9180,9180,9180,9189,9189,9202,9202,9202,9207,9207,9181,
9181,9181,9167,9167,9169,9169,9169,9163,9163,9164,9164,9164,9165,9165,9172,9172,
9172,9180,9180,9192,9192,9192,9178,9178,9161,9161,9161,9163,9163,9173,9173,9173,
9170,9170,9179,9179,9183,9183,9183,9196,9196,9207,9207,9207,9208,9208,9186,9186,
9186,9182,9182,9193,9193,9193,9197,9197,9188,9204,9204,9212,9212,9212,9223,9223,
9228,9228,9228,9235,9235,9215,9215,9215,9217,9217,9225,9225,9225,9230,9230,9237,
9237,9237,9246,9246,9260,9260,9260,9270,9270,9269,9269,9269,9256,9256,9256,9256,
9256,9263,9263,9274,9274,9274,9288,9288,9292,9292,9292,9307,9307,9310
)
    def __init__(self):
        self._i = 0
        self._step = 1

    def enable(self):
        pass

    def disable(self):
        pass

    def read_hrs(self):
        d = self.DATA[self._i]

        self._i += self._step
        if self._i >= len(self.DATA):
            self._i -= 1
            self._step = -1
        elif self._i < 0:
            self._i += 1
            self._step = 1

        return d

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
hrs = HRS()
rtc = RTC()
touch = CST816S(I2C(0), Pin('TP_INT', Pin.IN, quiet=True), Pin('TP_RST', Pin.OUT, quiet=True))
vibrator = Vibrator(Pin('MOTOR', Pin.OUT, value=0), active_low=True)

def connected():
    return not (int(rtc.uptime / 30) & 1)
