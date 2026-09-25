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
        self.active_low = active_low

    def pulse(self, duty=25, ms=40):
        """Briefly pulse the motor.

        :param int duty: Duty cycle, in percent.
        :param int ms:   Duration, in milliseconds.
        """
        if hasattr(PWM, 'FREQ_16MHZ'):
            # PWM API of the wasp-os fork of MicroPython (v1.12 based):
            # 16MHz clock with a period of 16000 ticks gives 1kHz.
            pwm = PWM(0, self.pin, freq=PWM.FREQ_16MHZ, duty=duty, period=16000)
        else:
            # Standard machine.PWM API of upstream MicroPython.
            pwm = PWM(self.pin, freq=1000, duty=duty)
        pwm.init()
        time.sleep_ms(ms)
        pwm.deinit()
        self.pin.value(self.active_low)
