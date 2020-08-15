# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 Daniel Thompson

"""Basic touch sensor driver
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

import array
import time
from machine import Pin
from watch import rtc

class TouchButton:
    """Simple touch controller driver.

    .. automethod:: __init__
    """

    def __init__(self, intr, rst, schedule=None):
        """Specify the bus used by the touch controller.

        :param machine.I2C bus: I2C bus for the CST816S.
        """
        self.tp_int = intr
        self.tp_rst = rst
        self.schedule = schedule
        self.event = array.array('H', (0, 0, 0))

        self._reset()
        self.tp_int.irq(trigger=Pin.IRQ_FALLING, handler=self.get_touch_data)

    def _reset(self):
        self.tp_rst.off()
        time.sleep_ms(5)
        self.tp_rst.on()
        time.sleep_ms(50)
        self.event[0] = 0
        self._wake_at = rtc.get_uptime_ms() + 300

    def get_touch_data(self, pin_obj):
        """Synthesize a right swipe during interrupt.
        """
        self.event[0] = 253 # NEXT

        if self.schedule:
            self.schedule(self)

    def get_event(self):
        """Receive a touch event.

        Check for a pending touch event and, if an event is pending,
        prepare it ready to go in the event queue.

        :return: An event record if an event is received, None otherwise.
        """
        if rtc.get_uptime_ms() < self._wake_at:
            self.event[0] = 0

        if self.event[0] == 0:
            return None

        return self.event

    def reset_touch_data(self):
        """Reset touch data.

        Reset touch data, call this function after processing an event.
        """
        self.event[0] = 0

    def wake(self):
        """Wake up touch controller chip.

        Just reset the chip in order to wake it up
        """
        self._reset()

    def sleep(self):
        """Put touch controller chip on sleep mode to save power.
        """
        self.tp_rst.off()

        # Ensure get_event() cannot return anything
        self.event[0] = 0
