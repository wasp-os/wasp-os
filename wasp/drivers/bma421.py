# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 Daniel Thompson

"""Bosch BMA421 accelerometer driver
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

import bma42x
import time
import motion
from machine import Pin

# Sensor orientation definition.
# The 6 most significant bits define the indexes of the x, y, and z values
# in the acceleration tuple returned by the sensor, while the 3 least
# significant bits define their sign (1 = keep original sign, 0 = negate).
#
#         Z index ─────────────────┐
#         Y index ───────────────┐ │
#         X index ─────────────┐ │ │
#                              ├┐├┐├┐
_DEFAULT_ORIENTATION = const(0b010010000)
#          1 = keep, 0 = negate      │││
#          X sign ───────────────────┘││
#          Y sign ────────────────────┘│
#          Z sign ─────────────────────┘

# Ref: BMA425 data sheet (register INT_STATUS_0)
_STATUS_MASK_WRIST_TILT = const(0b1000)

class BMA421:
    """BMA421 driver

    .. automethod:: __init__
    """
    def __init__(self, i2c, intr=None, orientation=_DEFAULT_ORIENTATION):
        """Configure the driver.

        :param machine.I2C i2c: I2C bus used to access the sensor.
        """
        self._dev = bma42x.BMA42X(i2c)
        self._orientation = orientation
        self._gesture_int = intr
        self._gesture_event = motion.AccelGestureEvent.NONE
        self.hardware_gesture_available = False

        if self._gesture_int != None:
            self._gesture_int.irq(trigger=Pin.IRQ_FALLING, handler=self.handle_interrupt)

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

        # Set axes remapping
        # This works only for hardware-based intelligence.
        # Software readout is remapped manually in accel_xyz().
        dev.set_remap_axes(self._orientation)

        self.hardware_gesture_available = dev.get_chip_id() == bma42x.BMA425_CHIP_ID

        # Enable gesture interrupts
        if self.hardware_gesture_available:
            dev.set_int_pin_config(int_line=bma42x.INTR1_MAP,
                                     edge_ctrl=bma42x.LEVEL_TRIGGER,
                                     lvl=bma42x.ACTIVE_LOW,
                                     od=bma42x.PUSH_PULL,
                                     output_en=True, input_en=False)
            dev.feature_enable(bma42x.WRIST_WEAR, True)
            dev.map_interrupt(bma42x.INTR1_MAP, bma42x.WRIST_WEAR_INT, True)

    def handle_interrupt(self, pin_obj):
        """Interrupt handler for gesture events originating from the sensor"""
        status = self._dev.read_int_status()
        if status & _STATUS_MASK_WRIST_TILT:
            self._gesture_event = motion.AccelGestureEvent.WRIST_TILT

    def get_gesture_event(self):
        """Receive the latest gesture event if any"""
        return self._gesture_event

    def reset_gesture_event(self):
        """Call after processing the gesture event"""
        self._gesture_event = motion.AccelGestureEvent.NONE

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
