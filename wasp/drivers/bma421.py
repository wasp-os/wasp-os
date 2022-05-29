# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 Daniel Thompson

"""Bosch BMA421 accelerometer driver
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

import bma42x
import time

# Sensor orientation definition.
# The 6 most significant bits define the indexes of the x, y, and z values
# in the acceleration tuple returned by the sensor, while the 3 least
# significant bits define their sign (1 = keep original sign, 0 = negate).
#
#         Z index ─────────────────┐
#         Y index ───────────────┐ │
#         X index ─────────────┐ │ │
#                              ├┐├┐├┐
_DEFAULT_ORIENTATION = const(0b010010101)
#          1 = keep, 0 = negate      │││
#          X sign ───────────────────┘││
#          Y sign ────────────────────┘│
#          Z sign ─────────────────────┘

class BMA421:
    """BMA421 driver

    .. automethod:: __init__
    """
    def __init__(self, i2c, orientation=_DEFAULT_ORIENTATION):
        """Configure the driver.

        :param machine.I2C i2c: I2C bus used to access the sensor.
        """
        self._dev = bma42x.BMA42X(i2c)
        self._orientation = orientation

    def reset(self):
        """Reset and reinitialize the sensor."""
        dev = self._dev

        # Init, reset, wait for reset, enable I2C watchdog
        dev.init()
        dev.set_command_register(0xb6)
        time.sleep(0.05)
        dev.set_reg(bma42x.NV_CONFIG_ADDR, 6);

        # Configure the sensor for basic step counting
        dev.write_config_file()
        dev.set_accel_enable(True)
        dev.set_accel_config(odr=bma42x.OUTPUT_DATA_RATE_100HZ,
                               range=bma42x.ACCEL_RANGE_2G,
                               bandwidth=bma42x.ACCEL_NORMAL_AVG4,
                               perf_mode=bma42x.CIC_AVG_MODE)
        dev.feature_enable(bma42x.STEP_CNTR, True)

    @property
    def steps(self):
        """Report the number of steps counted."""
        return self._dev.step_counter_output()

    @steps.setter
    def steps(self, value):
        if value != 0:
            raise ValueError()
        self._dev.reset_step_counter()

    def accel_xyz(self):
        """Return a triple with acceleration values"""
        raw = self._dev.read_accel_xyz()
        x = raw[self._orientation >> 7 & 0b11] * ((self._orientation >> 1 & 0b10) - 1)
        y = raw[self._orientation >> 5 & 0b11] * ((self._orientation      & 0b10) - 1)
        z = raw[self._orientation >> 3 & 0b11] * ((self._orientation << 1 & 0b10) - 1)
        return (x, y, z)
