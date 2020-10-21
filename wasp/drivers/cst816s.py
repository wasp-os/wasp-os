# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 Daniel Thompson

"""Hynitron CST816S touch contoller driver
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

import array
import time
from machine import Pin

class CST816S:
    """Hynitron CST816S I2C touch controller driver.

    .. automethod:: __init__
    """

    def __init__(self, bus, intr, rst, schedule=None):
        """Specify the bus used by the touch controller.

        :param machine.I2C bus: I2C bus for the CST816S.
        """
        self.i2c = bus
        self.tp_int = intr
        self.tp_rst = rst
        self.schedule = schedule
        self.dbuf = bytearray(6)
        self.event = array.array('H', (0, 0, 0))

        self._reset()
        self.tp_int.irq(trigger=Pin.IRQ_FALLING, handler=self.get_touch_data)

    def _reset(self):
        self.tp_rst.off()
        time.sleep_ms(5)
        self.tp_rst.on()
        time.sleep_ms(50)

    def get_touch_data(self, pin_obj):
        """Receive a touch event by interrupt.

        Check for a pending touch event and, if an event is pending,
        prepare it ready to go in the event queue.
        """
        dbuf = self.dbuf
        event = self.event

        try:
            self.i2c.readfrom_mem_into(21, 1, dbuf)
        except OSError:
            return None

        event[0] = dbuf[0] # event
        event[1] = ((dbuf[2] & 0xf) << 8) + dbuf[3] # x coord
        event[2] = ((dbuf[4] & 0xf) << 8) + dbuf[5] # y coord

        if self.schedule:
            self.schedule(self)

    def get_event(self):
        """Receive a touch event.

        Check for a pending touch event and, if an event is pending,
        prepare it ready to go in the event queue.

        :return: An event record if an event is received, None otherwise.
        """
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
        self.event[0] = 0

    def sleep(self):
        """Put touch controller chip on sleep mode to save power.
        """
        # Before we can send the sleep command we have to reset the
        # panel to get the I2C hardware running again...
        self._reset()
        try:
            self.i2c.writeto_mem(21, 0xa5, b'\x03')
        except:
            # If we can't power down then let's just put it in reset instead
            self.tp_rst.off()

        # Ensure get_event() cannot return anything
        self.event[0] = 0
