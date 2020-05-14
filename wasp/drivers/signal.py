# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 Daniel Thompson

"""Inverting pin wrapper
~~~~~~~~~~~~~~~~~~~~~~~~
"""

class Signal(object):
    """Simplified Signal class

    .. note::

        The normal C implementation of the Signal class used by MicroPython
        doesn't work on the nRF family. This class provides a temporary
        workaround until that can be addressed.

    .. automethod:: __init__
    """

    def __init__(self, pin, invert=False):
        """Create a Signal object by wrapping a pin."""
        self.pin = pin
        self.invert = invert

    def __call__(self, v=None):
        """Shortcut for :py:meth:`.value`"""
        return self.value(v)

    def value(self, v=None):
        """Get or set the state of the signal.

        :param v: Value to set, defaults to None (which means get the signal
                  state instead.
        :returns: The state of the signal if v is None, otherwise None.
        """
        if v == None:
            return self.invert ^ self.pin.value()
        self.pin.value(self.invert ^ bool(v))

    def on(self):
        """Activate the signal."""
        self.value(1)

    def off(self):
        """Deactivate the signal."""
        self.value(0)
