# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 Daniel Thompson

# Generic PWM capable vibrator

import time
from machine import PWM

class Vibrator(object):
    def __init__(self, pin, active_low=False):
        pin.value(active_low)
        self.pin = pin
        self.freq = PWM.FREQ_16MHZ
        self.period = 16000
        self.active_low = active_low

    def pulse(self, duty=50, ms=100):
        pwm = PWM(0, self.pin, freq=self.freq, duty=duty, period=self.period)
        pwm.init()
        time.sleep_ms(ms)
        pwm.deinit()
        self.pin.value(self.active_low)

