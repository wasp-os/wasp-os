# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 Daniel Thompson

import time
def sleep_ms(ms):
    time.sleep(ms / 1000)
time.sleep_ms = sleep_ms

import draw565

from machine import I2C
from machine import Pin
from machine import SPI

from drivers.cst816s import CST816S
from drivers.st7789 import ST7789_SPI
from drivers.vibrator import Vibrator


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
        self.uptime = 0

    def update(self):
        now = time.time()
        if now == self.uptime:
            return False
        self.uptime = now
        return True

    def get_localtime(self):
        return time.localtime()

    def get_time(self):
        now = time.localtime()
        return (now[3], now[4], now[5])

    def uptime(self):
        return time.time()

    def get_uptime_ms(self):
        return int(time.time() * 1000)

backlight = Backlight()
spi = SPI(0)
spi.init(polarity=1, phase=1, baudrate=8000000)
display = ST7789_SPI(240, 240, spi,
        cs=Pin("DISP_CS", Pin.OUT, quiet=True),
        dc=Pin("DISP_DC", Pin.OUT, quiet=True),
        res=Pin("DISP_RST", Pin.OUT, quiet=True))
drawable = draw565.Draw565(display)

battery = Battery()
button = Pin('BUTTON', Pin.IN, quiet=True)
rtc = RTC()
touch = CST816S(I2C(0))
vibrator = Vibrator(Pin('MOTOR', Pin.OUT, value=0), active_low=True)

