# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 Daniel Thompson

"""Heart rate monitor
~~~~~~~~~~~~~~~~~~~~~

A graphing heart rate monitor using a PPG sensor.

.. figure:: res/screenshots/HeartApp.png
    :width: 179

This program also implements some (entirely optional) debug features to
store the raw heart data to the filesystem so that the samples can be used
to further refine the heart rate detection algorithm.

To enable the logging feature select the heart rate application using the
watch UI and then run the following command via wasptool:

.. code-block:: sh

    ./tools/wasptool --eval 'wasp.system.app.debug = True'

Once debug has been enabled then the watch will automatically log heart
rate data whenever the heart rate application is running (and only
when it is running). Setting the debug flag to False will disable the
logging when the heart rate monitor next exits.

Finally to download the logs for analysis try:

.. code-block:: sh

    ./tools/wasptool --pull hrs.data
"""

import wasp
import machine
import ppg

class HeartApp():
    """Heart rate monitor application."""
    NAME = 'Heart'

    def __init__(self):
        self._debug = False
        self._hrdata = None

    def foreground(self):
        """Activate the application."""
        wasp.watch.hrs.enable()

        # There is no delay after the enable because the redraw should
        # take long enough it is not needed
        draw = wasp.watch.drawable
        draw.fill()
        draw.set_color(wasp.system.theme('bright'))
        draw.string('PPG graph', 0, 6, width=240)

        wasp.system.request_tick(1000 // 8)

        self._hrdata = ppg.PPG(wasp.watch.hrs.read_hrs())
        if self._debug:
            self._hrdata.enable_debug()
        self._x = 0

    def background(self):
        wasp.watch.hrs.disable()
        self._hrdata = None

    def _subtick(self, ticks):
        """Notify the application that its periodic tick is due."""
        draw = wasp.watch.drawable

        spl = self._hrdata.preprocess(wasp.watch.hrs.read_hrs())

        if len(self._hrdata.data) >= 240:
            draw.set_color(wasp.system.theme('bright'))
            draw.string('{} bpm'.format(self._hrdata.get_heart_rate()),
                        0, 6, width=240)

        # Graph is orange by default...
        color = wasp.system.theme('spot1')

        # If the maths goes wrong lets show it in the chart!
        if spl > 100 or spl < -100:
            color = 0xffff
        if spl > 104 or spl < -104:
            spl = 0
        spl += 104

        x = self._x
        draw.fill(0, x, 32, 1, 208-spl)
        draw.fill(color, x, 239-spl, 1, spl)
        if x < 238:
            draw.fill(0, x+1, 32, 2, 208)
        x += 2
        if x >= 240:
            x = 0
        self._x = x

    def tick(self, ticks):
        """This is an outrageous hack but, at present, the RTC can only
        wake us up every 125ms so we implement sub-ticks using a regular
        timer to ensure we can read the sensor at 24Hz.
        """
        t = machine.Timer(id=1, period=8000000)
        t.start()
        self._subtick(1)
        wasp.system.keep_awake()

        while t.time() < 41666:
            pass
        self._subtick(1)

        while t.time() < 83332:
            pass
        self._subtick(1)

        t.stop()
        del t

    @property
    def debug(self):
        return self._debug

    @debug.setter
    def debug(self, value):
        self._debug = value
        if value and self._hrdata:
            self._hrdata.enable_debug()
