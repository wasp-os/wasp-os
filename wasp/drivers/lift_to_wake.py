# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 Jannis Froese

"""A pseudo-device to handle lift-to-wake
~~~~~~~~~~~~~~~~~~~~~~~~
"""

class LiftToWake(object):
    """Lift-to-Wake handler

    .. a lift-to-wake implementation that uses an existing accelerometer without dedicated lift-to-wake support

    .. automethod:: __init__
    """

    def __init__(self, accelerometer, rtc):
        """Create a lift-to-wake handler"""
        self.accel = accelerometer
        self.rtc = rtc
        self._updateAt = rtc.get_uptime_ms()
        self.wakeCount = 0

    def update(self):
        """update internal state, returns true if device was lifted"""
        if self.rtc.get_uptime_ms() < self._updateAt:
            return False
        self._updateAt = self.rtc.get_uptime_ms() + 125

        (x, y, z) = self.accel.acceleration
        #print(y < 1 and y > -3 and x < -2 and z < -3 and z - x < -3 and z - x > -6, y < 1, y > -1, x < -2, z < -3, z-x < -3, z-x > -6, z-x, x, y, z)
        if y < 1 and y > -3  and x < -2 and z < -3 and z - x < -3 and z - x > -6:
            self.wakeCount += 1
            return True
        return False
