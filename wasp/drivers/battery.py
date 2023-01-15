# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 Daniel Thompson

"""Generic lithium ion battery driver
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
import micropython
# don't remove Pin import even though your IDE tells you it's unused, otherwise
# micropython can't load your battery level.
from machine import Pin, ADC
import array

class Battery(object):
    """Generic lithium ion battery driver.

    .. automethod:: __init__
    """

    def __init__(self, battery, charging, power=None):
        """Specify the pins used to provide battery status.

        :param Pin battery:  The ADC-capable pin that can be used to measure
                             battery voltage.
        :param Pin charging: A pin (or Signal) that reports the charger status.
        :param Pin power:    A pin (or Signal) that reports whether the device
                             has external power, defaults to None (which means
                             use the charging pin for power reporting too).
        """
        self._battery = ADC(battery)
        self._charging = charging
        self._power = power
        self._cache = array.array("I")

    @micropython.native
    def charging(self):
        """Get the charging state of the battery.

        :returns: True if the battery is charging, False otherwise.
        """
        return self._charging.value()

    def power(self):
        """Check whether the device has external power.

        :returns: True if the device has an external power source, False
                  otherwise.
        """
        if self._power:
            return self._power.value()
        return self._charging.value()

    def voltage_mv(self):
        """Read the battery voltage.

        Assumes a 50/50 voltage divider and a 3.3v power supply

        The last values is kept in a cache and only the minium cached value is
        shown to the user, this is to avoid the battery level
        going up and down because of the lack of precision of the mv.
        Note that this will underestimate battery level.

        :returns: Battery voltage, in millivolts.
        """
        raw = self._battery.read_u16()
        mv = (2 * 3300 * raw) // 65535
        cache = self._cache

        if self._charging.value():  # if charging, reset cache
            if len(cache):
                cache = array.array("I")
            return mv
        if len(cache) < 2:
            cache.append(mv)
            return mv
        if len(cache) > 2:  # should not happen
            cache = cache[-2:]
        if mv != cache[0] and mv != cache[1]:
            cache[0] = cache[1]
            cache[1] = mv
        return sum(cache) / 2

    def level(self):
        """Estimate the battery level.

        The current the estimation approach is extremely simple. It is assumes
        the discharge from 4v to 3.5v is roughly linear and 4v is 100% and
        that 3.5v is 5%. Below 3.5v the voltage will start to drop pretty
        sharply so we will drop from 5% to 0% pretty fast... but we'll
        live with that for now.

        :returns: Estimate battery level in percent.
        """
        mv = self.voltage_mv()
        level = int((mv - 3500) / (700) * 100)  # 0.7V is 4.2-3.5V
        return min(100, max(0, level))
