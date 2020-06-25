# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 Daniel Thompson

"""Watch driver instances
~~~~~~~~~~~~~~~~~~~~~~~~~

.. data:: watch.backlight

    Backlight driver, typically a board specific driver with a single
    :py:meth:`set` method.

.. data:: watch.battery

    Battery driver, typically the generic metering driver,
    :py:class:`drivers.battery.Battery`.

.. data:: watch.button

    An instance of machine.Pin (or a signal) that an application can use
    to poll the state of the hardware button.

.. data:: watch.display

    Display driver, typically :py:class:`drivers.st7789.ST7789_SPI`.

.. data:: watch.drawable

    Drawing library for :py:data:`watch.display`. It will be adapted to match the
    bit depth of the display, :py:class:`draw565.Draw565` for example.

.. data:: watch.rtc

    RTC driver, typically :py:class:`drivers.nrf_rtc.RTC`.

.. data:: watch.touch

    Touchscreen driver, for example :py:class:`drivers.cst816s.CST816S`.

.. data:: watch.vibrator

    Vibration motor driver, typically :py:class:`drivers.vibrator.Vibrator`.
"""

import time
def sleep_ms(ms):
    time.sleep(ms / 1000)
time.sleep_ms = sleep_ms

class Accel():
    def reset(self):
        pass

class Pin():
    def value(v=None):
        pass

accel = Accel()
button = Pin()
