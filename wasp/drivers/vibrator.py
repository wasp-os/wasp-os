# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 Daniel Thompson

"""Generic PWM capable vibration motor driver
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

import time
from machine import PWM

class Vibrator(object):
    """Vibration motor driver.

    .. automethod:: __init__
    """
    def __init__(self, pin, active_low=False):
        """Specify the pin and configuration used to operate the motor.

        :param machine.Pin pin: The PWM-capable pin used to driver the
                                vibration motor.
        :param bool active_low: Invert the resting state of the motor.
        """
        pin.value(active_low)
        self.pin = pin
        self.freq = PWM.FREQ_16MHZ
        self.period = 16000
        self.active_low = active_low

    def pulse(self, duty=25, ms=40):
        """Briefly pulse the motor.

        :param int duty: Duty cycle, in percent.
        :param int ms:   Duration, in milliseconds.
        """
        pwm = PWM(0, self.pin, freq=self.freq, duty=duty, period=self.period)
        pwm.init()
        time.sleep_ms(ms)
        pwm.deinit()
        self.pin.value(self.active_low)
