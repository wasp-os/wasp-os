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
        self._pwm = None
        self._busy = False

    def _ensure_pwm(self):
        if self._pwm is None:
            if hasattr(PWM, 'FREQ_16MHZ'):
                # PWM API of the wasp-os fork of MicroPython (v1.12 based):
                # 16MHz clock with a period of 16000 ticks gives 1kHz.
                self._pwm = PWM(0, self.pin, freq=PWM.FREQ_16MHZ, duty=0,
                                 period=16000)
            else:
                # Standard machine.PWM API of upstream MicroPython. Without
                # invert a duty of 0 holds the pin low, which switches an
                # active low motor fully on.
                self._pwm = PWM(self.pin, freq=1000, duty=0,
                                invert=self.active_low)
            self._pwm.init()
        return self._pwm

    def pulse(self, duty=25, ms=40):
        """Briefly pulse the motor.

        :param int duty: Duty cycle, in percent.
        :param int ms:   Duration, in milliseconds.
        """
        # Guard against re-entrant/overlapping calls (e.g. from a touch
        # driver that -- despite its own best efforts at debouncing --
        # still ends up calling pulse() again before a previous call has
        # finished its sleep_ms()): only one call is ever allowed to
        # actually be driving the motor at a time, and any call that
        # arrives while one is already in progress is simply dropped
        # rather than restarting/extending the buzz.
        if self._busy:
            return
        self._busy = True
        try:
            pwm = self._ensure_pwm()
            pwm.duty(duty)
            time.sleep_ms(ms)
        finally:
            # Release the PWM device after every pulse (the nRF52832 only
            # has three) and hand the pin back to plain GPIO in its resting
            # state. This runs in a finally so that the motor is switched
            # off even if a scheduled callback raises during the sleep_ms().
            if self._pwm is not None:
                self._pwm.deinit()
                self._pwm = None
            self.pin.value(self.active_low)
            self._busy = False
