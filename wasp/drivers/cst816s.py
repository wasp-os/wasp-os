"""Hynitron CST816S touch contoller driver for MicroPython."""

class CST816S:
    """Hynitron CST816S I2C touch controller driver."""
    
    def __init__(self, bus):
        self.i2c = bus
        self.dbuf = bytearray(6)

    def get_event(self, queue):
        """Receive a touch event.

        Check for a pending touch event and, if an event is pending,
        prepare it ready to go in the event queue.

        :return: True if an event is received, False otherwise.
        """
        dbuf = self.dbuf

        try:
            self.i2c.readfrom_mem_into(21, 1, dbuf)
        except OSError:
            return False

        queue[0] = dbuf[0]
        queue[1] = ((dbuf[2] & 0xf) << 8) + dbuf[3]
        queue[2] = ((dbuf[4] & 0xf) << 8) + dbuf[5]
        return True
