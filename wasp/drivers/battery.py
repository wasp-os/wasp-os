# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 Daniel Thompson

# Generic lithium ion battery driver

from machine import Pin, ADC

class Battery(object):
    def __init__(self, battery, charging, power=None):
        self._battery = ADC(battery)
        self._charging = charging
        self._power = power

    def charging(self):
        return self._charging.value() 

    def power(self):
        if self._power:
            return self._power.value()
        return self._charging.value()

    def voltage_mv(self):
        # Assumes a 50/50 voltage divider and a 3.3v power supply
        raw = self._battery.read_u16()
        return (2 * 3300 * raw) // 65535

    def level(self):
        # This is a trivial battery level estimation approach. It is assumes
        # the discharge from 4v to 3.5v is roughly linear and 4v is 100% and
        # that 3.5v is 5%. Below 3.5v the voltage will start to drop pretty
        # sharply to we will drop from 5% to 0% pretty fast... but we'll
        # live with that for now.
        mv = self.voltage_mv()
        level = ((19 * mv) // 100) - 660
        if level > 100:
            return 100
        if level < 0:
            return 0
        return level
