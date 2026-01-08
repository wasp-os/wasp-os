# MIT License
#
# Copyright (c) 2020 Carlos Gil Gonzalez
#
# This file is part of MicroPython SC7A20 driver
#
# Licensed under the MIT license:
#   http://www.opensource.org/licenses/mit-license.php
# Based on:
# Copyright (c) 2017-2018 Mika Tuupola
# https://github.com/tuupola/micropython-lis2hh12
# Defconfurs
# https://github.com/defconfurs/dcfurs-badge-dc27/blob/master/lis2de12.py
# Julian Finn
# https://github.com/hdsjulian/micropov/blob/master/lis3dh.py
#

"""
MicroPython I2C driver for SC7A20 3-axis accelerometer
"""

import struct
import time
from micropython import const
from machine import Pin
from collections import namedtuple
import math

__version__ = "0.0.1"

# pylint: disable=bad-whitespace
_TEMP_L = const(0x0c)
_TEMP_H = const(0x0d)
_TEMPCFG = const(0x1f)
_WHO_AM_I = const(0x0f)  # 0b00010001 = 0x11
_CTRL1 = const(0x20)
_CTRL2 = const(0x21)
_CTRL3 = const(0x22)
_CTRL4 = const(0x23)
_CTRL5 = const(0x24)
_CTRL6 = const(0x25)
_REFERENCE = const(0x26)
_STATUS = const(0x27)
_OUT_X_L = const(0x28)
_OUT_X_H = const(0x29)
_OUT_Y_L = const(0x2a)
_OUT_Y_H = const(0x2b)
_OUT_Z_L = const(0x2c)
_OUT_Z_H = const(0x2d)
_REG_INT1SRC = const(0x31)
_REG_CLICKCFG = const(0x38)
_REG_CLICKSRC = const(0x39)
_REG_CLICKTHS = const(0x3A)
_REG_TIMELIMIT = const(0x3B)
_REG_TIMELATENCY = const(0x3C)
_REG_TIMEWINDOW = const(0x3D)

WHOAMI = const(0x11)

# CTRL1 # SAMPLING FREQUENCY / OPTION DATA RATE
# [ODR3 ODR2 ODR1 ODR0 LPen Zen Yen Xen]
_ODR_MASK = const(0b00000111)  # Zen, Yen, Xen set to 1 to enable
_LP_MASK = const(0b00001000)
ODR_OFF = const(0b00000000)  # Power Down
ODR_1HZ = const(0b00010000)
ODR_10HZ = const(0b00100000)
ODR_25HZ = const(0b00110000)
ODR_50HZ = const(0b01000000)
ODR_100HZ = const(0b01010000)
ODR_200HZ = const(0b01100000)
ODR_400HZ = const(0b01110000)
ODR_1600HZ = const(0b10001000)  # Low power mode (1.6 KHz)
ODR_1250HZ = const(0b10010000)  # Normal working mode (1.25 kHz) / Low power mode (5 KHz)

# CTRL4 # FULL-SCALE RANGE (+-2g/4g/8g/16g)
# BDU BLE FS1 FS0 HR ST1 ST0 SIM; FS1, FS0 --> FULL-SCALE SELECTION
# _FS_MASK = const(0b00110000)
# all in HIGH-RES MODE
FS_2G = const(0b10001000)  # 1:BDU, 0:LE, 00: FS-2G, 1:HR, 000
FS_4G = const(0b10011000)
FS_8G = const(0b10101000)
FS_16G = const(0b10111000)

# MECHANICAL CHARACTERISTICS
# SENSITIVITY
# X mg / (2 ** 11) = x mg/level or digit (2**11 --> 12 bit but signed so 11)
_SO_2G = (2000) / (2 ** 11)  # ~1 mg / digit
_SO_4G = (4000) / (2 ** 11)  # ~2 mg / digit
_SO_8G = (8000) / (2 ** 11)  # ~4 mg / digit
_SO_16G = (16000) / (2 ** 11)  # ~8 mg / digit

# ACCEL UNIT
SF_G = 0.001  # 1 mg = 0.001 g
SF_SI = 0.00980665  # 1 mg = 0.00980665 m/s2
STANDARD_GRAVITY = 9.806
AccelgTuple = namedtuple("acceleration_g", ("x", "y", "z"))
AccelSITuple = namedtuple("acceleration_ms2", ("x", "y", "z"))


class Offset:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def __repr__(self):

        return "AccelOffset(x={}, y={}, z={})".format(self.x, self.y, self.z)


class SC7A20:
    """Class which provides interface to SC7A20 3-axis accelerometer."""

    def __init__(self, i2c=None, irq1='ACCEL_INT', irq2=None,
                 address=0x18, odr=ODR_100HZ, fs=FS_2G, sf=SF_G, debug=True):

        # Acceleration data is 12 bit left justified:
        # INT: ACCEL_INT (P8)
        self.i2c = i2c
        self.buf_confg = bytearray(1)
        self._x_buff = bytearray(2)  # 12 bit needs 2 bytes # AXIS 0
        self._y_buff = bytearray(2)  # AXIS 1
        self._z_buff = bytearray(2)  # AXIS 2
        self.address = address
        self.range = fs
        self.steps = 0

        if WHOAMI != self.whoami:
            raise RuntimeError("SC7A20 not found in I2C bus.")
        else:
            if debug:
                print("SC7A20 [%s] 3-axis accelerometer at [%s]" % (hex(WHOAMI),
                                                                    hex(self.address)))

        self._sf = sf
        self._so = _SO_2G
        self._offst = Offset(0, 0, 0)
        self.init_confg()
        # Initialise interrupt pins
        self._int1 = None
        self._int2 = None  # use this for calibration routine
        if irq1:
            self._int1 = Pin(irq1, Pin.IN)
        if irq2:
            self._int2 = Pin(irq2, Pin.IN)

    def _write_register(self, register, value):
        self.buf_confg[0] = value
        self.i2c.writeto_mem(self.address, register, self.buf_confg)

    def _read_register(self, register):
        self.i2c.readfrom_mem_into(self.address, register, self.buf_confg)
        return (self.buf_confg[0])

    def _set_odr(self, value):
        self._write_register(_CTRL1, _ODR_MASK | value)

    def _set_fs(self, value):
        self._write_register(_CTRL4, value)
        self.range = self._read_register(_CTRL4)
        # Store the sensitivity multiplier
        if FS_2G == self.range:
            self._so = _SO_2G
        elif FS_4G == self.range:
            self._so = _SO_4G
        elif FS_8G == self.range:
            self._so = _SO_8G
        elif FS_16G == self.range:
            self._so = _SO_16G

    def init_confg(self):
        # Configure and enable the acceleromter
        # Reboot
        self._write_register(_CTRL5, 0x80)
        time.sleep(0.01)  # takes 5ms

        # Enable all axes, normal mode.
        # self._write_register(_CTRL1, 0x07)
        self._set_odr(ODR_100HZ)  # Enable the device and configure 100Hz sampling.
        # High res & BDU enabled.
        self._set_fs(FS_2G)  # +/- 2g full scale mode.
        # self._write_register(_CTRL4, 0x88)
        # Enable ADCs.
        self._write_register(_TEMPCFG, 0x80)
        # Latch interrupt for INT1
        self._write_register(_CTRL5, 0x08)

    def power_off(self):
        self._set_odr(ODR_OFF)
        self._read_register(_REFERENCE)  # Reset filter block

    def reset(self):
        self.power_off()
        self.init_confg()

    def _read_accel_raw(self):
        self._x_buff[:] = (self.i2c.readfrom_mem(self.address, _OUT_X_L, 1) +
                           self.i2c.readfrom_mem(self.address, _OUT_X_H, 1))
        self._y_buff[:] = (self.i2c.readfrom_mem(self.address, _OUT_Y_L, 1) +
                           self.i2c.readfrom_mem(self.address, _OUT_Y_H, 1))
        self._z_buff[:] = (self.i2c.readfrom_mem(self.address, _OUT_Z_L, 1) +
                           self.i2c.readfrom_mem(self.address, _OUT_Z_H, 1))
        return (struct.unpack('<hhh', self._x_buff + self._y_buff + self._z_buff))

    def calibrate(self, x=False, y=False, z=False, all=False):
        # See Figure 14: 6D recognized positions

        if not self._int2:
            print('irq2 Interrupt must be setted for this method')
        else:
            if all:
                x, y, z = True, True, True
            if z:
                # Z calibration TOP-BOTTOM
                print('Calibration of Z axis:')
                print('Put accel in Top position (e) and then push interrupt')
                while not self._int2.value():
                    time.sleep(0.1)
                time.sleep(1)
                self.accel()
                self.accel()
                z_acc = self.accel().z
                z_top = (-1) - z_acc  # must be -1 g
                print("ZTop: Expected -1.0 , got: {}".format(z_acc))
                time.sleep(0.5)
                print('Put accel in Bottom position (f) and then push interrupt')
                while not self._int2.value():
                    time.sleep(0.1)
                time.sleep(1)
                self.accel()
                self.accel()
                z_acc = self.accel().z
                z_bot = (1) - z_acc  # must be 1g
                print("ZBott: Expected 1.0 , got: {}".format(z_acc))
                self._offst.z += (z_top + z_bot) / 2
                print('Z offset: {}'.format(self._offst.z))

            if x:
                # Z calibration TOP-BOTTOM
                print('Calibration of X axis:')
                print('Put accel in Top position (e) and then push interrupt')
                while not self._int2.value():
                    time.sleep(0.1)
                time.sleep(1)
                self.accel()
                self.accel()
                x_acc = self.accel().x
                x_top = (-1) - x_acc  # must be -1 g
                print("XTop: Expected -1.0 , got: {}".format(x_acc))
                time.sleep(0.5)
                print('Put accel in Bottom position (f) and then push interrupt')
                while not self._int2.value():
                    time.sleep(0.1)
                time.sleep(1)
                self.accel()
                self.accel()
                x_acc = self.accel().x
                x_bot = (1) - x_acc  # must be 1g
                print("XBott: Expected 1.0 , got: {}".format(x_acc))
                self._offst.x += (x_top + x_bot) / 2
                print('X offset: {}'.format(self._offst.x))
            if y:
                # Z calibration TOP-BOTTOM
                print('Calibration of Y axis:')
                print('Put accel in Top position (e) and then push interrupt')
                while not self._int2.value():
                    time.sleep(0.1)
                time.sleep(1)
                self.accel()
                self.accel()
                y_acc = self.accel().y
                y_top = (-1) - y_acc  # must be -1 g
                print("YTop: Expected -1.0 , got: {}".format(y_acc))
                time.sleep(0.5)
                print('Put accel in Bottom position (f) and then push interrupt')
                while not self._int2.value():
                    time.sleep(0.1)
                time.sleep(1)
                self.accel()
                self.accel()
                y_acc = self.accel().y
                y_bot = (1) - y_acc  # must be 1g
                print("YBott: Expected 1.0 , got: {}".format(y_acc))
                self._offst.y += (y_top + y_bot) / 2
                print('Y offset: {}'.format(self._offst.y))

            print('Calibration Done!')

    def accel(self):
        """
        Acceleration measured by the sensor. By default will return a
        3-tuple of X, Y, Z axis acceleration values in device.unit (default (g))
        """
        _x, _y, _z = self._read_accel_raw()
        x = (_x >> 4) * self._so * self._sf + self._offst.x
        y = (_y >> 4) * self._so * self._sf + self._offst.y
        z = (_z >> 4) * self._so * self._sf + self._offst.z
        if self._sf == SF_SI:
            return AccelSITuple(x, y, z)
        else:
            return AccelgTuple(x, y, z)

    def stream_accel(self, st_time=10, sleep_ms=100):
        t0 = 0
        while t0 < (st_time * 1000):
            acc = self.accel()
            print('X: {} Y: {} Z: {}'.format(acc.x, acc.y, acc.z))
            time.sleep_ms(sleep_ms)
            t0 += sleep_ms

    @property
    def whoami(self):
        """ Value of the whoami register. """

        return self._read_register(_WHO_AM_I)

    @property
    def unit(self):
        """Unit of accelerometer data"""
        if self._sf == SF_G:
            return 'g'
        elif self._sf == SF_SI:
            return 'm/s^2'

    @unit.setter
    def unit(self, unit):
        if unit == 'g':
            self._sf = SF_G
        elif unit == 'SI' or unit == 'm/s^2':
            self._sf = SF_SI

    @property
    def acceleration(self):
        """The x, y, z acceleration values returned in a 3-tuple and are in m / s ^ 2."""
        accel_range = self.range
        if accel_range == ((FS_16G >> 4) & 0x03):
            divider = 1365
        elif accel_range == ((FS_8G >> 4) & 0x03):
            divider = 4096
        elif accel_range == ((FS_4G >> 4) & 0x03):
            divider = 8190
        elif accel_range == ((FS_2G >> 4) & 0x03):
            divider = 16380

        x, y, z = struct.unpack('<hhh',
                                self.i2c.readfrom_mem(self.address, _OUT_X_L | 0x80, 6))

        # convert from Gs to m / s ^ 2 and adjust for the range
        x = ((x / divider) + self._offst.x) * STANDARD_GRAVITY
        y = ((y / divider) + self._offst.y) * STANDARD_GRAVITY
        z = ((z / divider) + self._offst.z) * STANDARD_GRAVITY
        return AccelSITuple(x, y, z)

    @property
    def data_rate(self):
        """The data rate of the accelerometer:
            (1): 1 Hz, (2): 10 Hz, (3): 25 Hz,
            (4): 50 Hz, (5): 100 Hz, (6): 200 Hz
            (7): 400 Hz, (8): 1.6 KHz (LP), (9): 1.25 KHz/5 KHz (LP)
            """
        ctl1 = self._read_register(_CTRL1)
        return ctl1 >> 4

    @data_rate.setter
    def data_rate(self, rate):
        ctl1 = self._read_register(_CTRL1)
        ctl1 & 0x0f  # get [B3-B0] for current LPen Zen Yen Xen configuration
        ctl1 |= rate << 4  # SHIFT RATE 4 bits LEFT AND MASK for final configuration
        self._write_register(_CTRL1, ctl1)

    @property
    def range(self):
        """The full scale range of the accelerometer:
        (0): +/- 2g, (1): +/- 4g, (2): +/- 8g, (3): +/- 16g
        """
        ctl4 = self._read_register(_CTRL4)
        return (ctl4 >> 4) & 0x03

    @range.setter
    def range(self, range_value):
        ctl4 = self._read_register(_CTRL4)
        ctl4 &= 0xcf  # clear fs0 fs1, save the rest (bdu, ble , st0, st1, sim)
        ctl4 |= range_value << 4
        self._write_register(_CTRL4, ctl4)

    @property
    def power_mode(self):
        """0: Normal mode: 0, High-Resolution: 1, Low-Power: 2"""
        ctrl1 = ((self._read_register(_CTRL1) & 0b1000) >> 3) << 1
        ctrl4 = (self._read_register(_CTRL4) & 0b1000) >> 3
        return ctrl1 | ctrl4

    @power_mode.setter
    def power_mode(self, value):
        """0: Normal mode, 1: High-Resolution, 2: Low-Power"""
        # CTRL_REG1[3] CTRL_REG4[3]
        #  (LPen bit)  (HR bit)
        # LP:  1           0
        # N:   0           0
        # HR:  0           1
        if value == 0:
            ctrl1 = self._read_register(_CTRL1) & 0b11110111
            self._write_register(_CTRL1, ctrl1)
            ctrl4 = self._read_register(_CTRL4) & 0b11110111
            self._write_register(_CTRL4, ctrl4)
        elif value == 1:
            ctrl1 = self._read_register(_CTRL1) & 0b11110111
            self._write_register(_CTRL1, ctrl1)
            ctrl4 = self._read_register(_CTRL4) | 0b1000
            self._write_register(_CTRL4, ctrl4)
        elif value == 2:
            ctrl1 = self._read_register(_CTRL1) | 0b1000
            self._write_register(_CTRL1, ctrl1)
            ctrl4 = self._read_register(_CTRL4) & 0b11110111
            self._write_register(_CTRL4, ctrl4)

    def shake(self, shake_threshold=30, avg_count=10, total_delay=0.1):
        """
        Detect when the accelerometer is shaken.
         """
        shake_accel = (0, 0, 0)
        for _ in range(avg_count):
            shake_accel = tuple(map(sum, zip(shake_accel, self.acceleration)))
            time.sleep(total_delay / avg_count)
        avg = tuple(value / avg_count for value in shake_accel)
        total_accel = math.sqrt(sum(map(lambda x: x * x, avg)))
        return total_accel > shake_threshold

    @property
    def tapped(self):
        """
        True if a tap was detected recently. Whether its a single tap or double tap is
        determined by the tap param on ``set_tap``. ``tapped`` may be True over
        multiple reads even if only a single tap or single double tap occurred if the
        interrupt (int) pin is not specified.

        """
        if self._int1 and not self._int1.value():
            return False
        raw = self._read_register(_REG_CLICKSRC)
        TAP = raw >> 6
        if TAP:
            return True
        else:
            return False

    def set_tap(self, tap, threshold=80, time_limit=51, time_latency=20,
                time_window=255, click_cfg=None):
        """
        The tap detection parameters.
        0 to disable tap detection, 1 to detect only single
                        taps, and 2 to detect only double taps.
        threshold:1 LSB = full scale/128. e.g. 72 * (2/127) --> 1.13 g
        TIME: [1 LSB = 1/ODR (s)] e.g. : 51 * 1/400 * 1000 --> 127.5 ms,
        """
        if (tap < 0 or tap > 2) and click_cfg is None:
            raise ValueError('Tap must be 0 (disabled), 1 (single tap), or 2 (double tap)!')
        if threshold > 127 or threshold < 0:
            raise ValueError('Threshold out of range (0-127)')

        ctrl3 = self._read_register(_CTRL3)
        if tap == 0 and click_cfg is None:
            # Disable click interrupt.
            self._write_register(_CTRL3, ctrl3 & ~(0x80))  # Turn off I1_CLICK.
            self._write_register(_REG_CLICKCFG, 0)
            return
        else:
            self.data_rate = 7  # 0b111 --> 400 Hz ODR for click detection
            self.power_mode = 2  # LOW POWER
            self._write_register(_CTRL3, ctrl3 | 0x80)  # Turn on int1 click output
            self._write_register(_CTRL5, 0x08)  # latch interrupt on int1

        if click_cfg is None:
            if tap == 1:
                click_cfg = 0x15  # Turn on all axes & singletap.
            if tap == 2:
                click_cfg = 0x2A  # Turn on all axes & doubletap.
        # Or, if a custom click configuration register value specified, use it.
        self._write_register(_REG_CLICKCFG, click_cfg)
        self._write_register(_REG_CLICKTHS, 0x80 | threshold)
        self._write_register(_REG_TIMELIMIT, time_limit)
        self._write_register(_REG_TIMELATENCY, time_latency)
        self._write_register(_REG_TIMEWINDOW, time_window)

    def wait_tap(self, wait_s=10, debug_click=True, rintsrc=False):
        t0 = 0
        while t0 < (wait_s * 1000):
            int1_val = 0
            int2_val = 0
            if self._int1:
                int1_val = self._int1.value()
            if self._int2:
                int2_val = self._int2.value()
            raw = self._read_register(_REG_CLICKSRC)
            if rintsrc:
                self._read_register(_REG_INT1SRC)
            TAP = raw >> 6
            click_type = (raw & 0b00110000) >> 4  # SINGLE: 1, DOUBLE: 2
            if click_type == 1:
                click_type = 'Single'
            elif click_type == 2:
                click_type = 'Double'
            sign = (raw & 0b1000) >> 3
            if sign == 1:
                sign = '+'
            elif sign == 0:
                sign = '-'
            z = (raw & 0b100) >> 2
            y = (raw & 0b10) >> 1
            x = (raw & 0b1)
            dbg_info = "Type: {}, Sign: {}, Axis: [X:{}, Y:{}, Z:{}]".format(click_type,
                                                                             sign,
                                                                             x, y, z)
            # get if click event, single, sign, axis, interrupts
            if TAP:
                if not debug_click:
                    print('Clicked!')
                else:
                    print('Clicked: ', dbg_info)
                    print('Int1: {} ; Int2: {}'.format(int1_val, int2_val))
            time.sleep_ms(100)
            t0 += 100
