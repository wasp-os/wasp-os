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
        self._gesture_released = True
        self._last_gesture_ms = -1000000

        self._reset()
        self.tp_int.irq(trigger=Pin.IRQ_FALLING, handler=self.get_touch_data)

    def _reset(self):
        self.tp_rst.off()
        time.sleep_ms(5)
        self.tp_rst.on()
        time.sleep_ms(50)

    def version(self):
        self.wake()
        v = self.i2c.readfrom_mem(21, 0xa6, 4)
        self.sleep()
        return v

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

        raw = dbuf[0]

        # dbuf[1] is the touch point count register (see e.g. InfiniTime's
        # Cst816s.h touchPointNumIndex): the low nibble is the number of
        # fingers currently in contact with the screen, independent of
        # dbuf[0]'s gesture code.
        touching = (dbuf[1] & 0x0f) > 0

        # Directional swipe (event codes 1-4; 5 is a plain touch/drag,
        # never gated since e.g. dragging a Slider needs a fresh
        # coordinate on every sample). The CST816S's on-chip gesture
        # recognizer does not report a slide exactly once per physical
        # swipe: confirmed on real hardware, during a single continuous
        # drag it keeps reporting a gesture code -- and can even alternate
        # between different ones (e.g. UP, a plain TOUCH, then DOWN) --
        # for as long as contact continues, sometimes well beyond the
        # duration of a normal swipe motion.
        #
        # InfiniTime's TouchHandler::ProcessTouchInfo works around the
        # same chip behaviour with a "gestureReleased" latch: once a slide
        # gesture has been accepted, further ones are ignored until the
        # touch point count goes back to 0 (the finger is lifted). Using
        # *only* that latch turned out to be unsafe here, though: this
        # chip does not reliably generate any further interrupt at all
        # once a gesture has been reported and the finger stays down or
        # is lifted without further movement -- confirmed on real
        # hardware, a swipe worked exactly once and then never again
        # until reset, because we were waiting for a "touching went back
        # to 0" event that never arrived to reopen the latch. So the
        # latch is combined with a time-based fallback: it still reopens
        # immediately on a genuine observed release (for quick, responsive
        # back-to-back swipes), but reopens after a fixed cooldown
        # regardless, so a release that is never reported can't leave
        # swiping permanently dead.
        if not touching:
            self._gesture_released = True

        if 0 < raw < 5:
            if not touching:
                return
            now = time.ticks_ms()
            if not self._gesture_released and \
                    time.ticks_diff(now, self._last_gesture_ms) < 300:
                return
            self._gesture_released = False
            self._last_gesture_ms = now

        if raw == 0:
            return

        event[0] = raw # event
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
        self._gesture_released = True

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
        self._gesture_released = True
