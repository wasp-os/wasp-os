# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 Daniel Thompson

"""Hynitron CST816S touch contoller driver for MicroPython.

After modifying this file we can test the changes by replacing the
frozen driver with the modified driver. The following command will
upload the code and integrate it into the watch namespace::

    ./tools/wasptool\
      --exec wasp/drivers/cst816s.py\
      --eval "watch.touch = CST816S(watch.i2c)"`
"""

import array

class CST816S:
    """Hynitron CST816S I2C touch controller driver."""
    
    def __init__(self, bus):
        self.i2c = bus
        self.dbuf = bytearray(6)
        self.event = array.array('H', (0, 0, 0))

    def get_event(self):
        """Receive a touch event.

        Check for a pending touch event and, if an event is pending,
        prepare it ready to go in the event queue.

        :return: An event record if an event is received, None otherwise.
        """
        dbuf = self.dbuf
        event = self.event

        # TODO: check the interrupt pin

        try:
            self.i2c.readfrom_mem_into(21, 1, dbuf)
        except OSError:
            return None

        # Skip junk events
        if dbuf[0] == 0:
            return None

        x = ((dbuf[2] & 0xf) << 8) + dbuf[3]
        y = ((dbuf[4] & 0xf) << 8) + dbuf[5]
        swipe_start = dbuf[2] & 0x80
        
        # Skip identical events... when the I2C interface comes alive
        # we can still get back stale events
        if dbuf[0] == event[0] and x == event[1] and y == event[2] \
                and not swipe_start:
            return None

        # This is a good event, lets save it
        event[0] = dbuf[0]
        event[1] = x
        event[2] = y

        # Do not forward swipe start events
        if dbuf[2] & 0x80:
            event[0] = 0
            return None

        return event
