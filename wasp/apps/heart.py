# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 Daniel Thompson

import wasp
import machine

class Biquad():
    """Direct Form II Biquad Filter"""

    def __init__(self, b0, b1, b2, a1, a2):
        self._coeff = (b0, b1, b2, a1, a2)
        self._v1 = 0
        self._v2 = 0

    def step(self, x):
        c = self._coeff
        v1 = self._v1
        v2 = self._v2

        v = x - (c[3] * v1) - (c[4] * v2)
        y = (c[0] * v) + (c[1] * v1) + (c[2] * v2)

        self._v2 = v1
        self._v1 = v
        return y

class PTAGC():
    """Peak Tracking Automatic Gain Control
    
    In order for the correlation checks to work correctly we must
    aggressively reject spikes caused by fast DC steps. Setting a
    threshold based on the median is very effective at killing
    spikes but needs an extra 1k for sample storage which isn't
    really plausible for a microcontroller.
    """
    def __init__(self, start, decay, threshold):
        self._peak = start
        self._decay = decay
        self._boost = 1 / decay
        self._threshold = threshold

    def step(self, spl):        
        # peak tracking
        peak = self._peak
        if abs(spl) > peak:
            peak *= self._boost
        else:
            peak *= self._decay
        self._peak = peak

        # rejection filter (clipper)
        threshold = self._threshold
        if spl > (peak * threshold) or spl < (peak * -threshold):
            return 0
        
        # booster
        spl = 100 * spl / (2 * peak)
        
        return spl

class HeartApp():
    """Heart Rate Sensing application.

    """
    NAME = 'Heart'

    def foreground(self):
        """Activate the application."""
        wasp.watch.hrs.enable()

        # There is no delay after the enable because the redraw should
        # take long enough it is not needed
        draw = wasp.watch.drawable
        draw.fill()
        draw.string('PPG graph', 0, 6, width=240)

        self._hpf = Biquad(0.87518309, -1.75036618,  0.87518309, -1.73472577,  0.7660066)
        self._agc = PTAGC(20, 0.971, 2)
        self._lpf = Biquad(0.10873253, 0.21746505, 0.10873253, -0.76462555,  0.19955565)

        self._x = 0
        self._offset = wasp.watch.hrs.read_hrs()

        wasp.system.request_tick(1000 // 8)

    def background(self):
        wasp.watch.hrs.disable()
        del self._hpf
        del self._agc
        del self._lpf

    def _tick(self, ticks):
        """Notify the application that its periodic tick is due."""
        spl = wasp.watch.hrs.read_hrs()
        spl -= self._offset
        spl = self._hpf.step(spl)
        spl = self._agc.step(spl)
        spl = self._lpf.step(spl)

        color = 0xffc0

        # If the maths goes wrong lets show it in the chart!
        if spl > 100 or spl < -100:
            color = 0xffff
        if spl > 104 or spl < -104:
            spl = 0
        spl = int(spl) + 104

        x = self._x

        draw = wasp.watch.drawable
        draw.fill(0, x, 32, 1, 208-spl)
        draw.fill(color, x, 239-spl, 1, spl)

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
        self._tick(1)
        wasp.system.keep_awake()

        while t.time() < 41666:
            pass
        self._tick(1)

        while t.time() < 83332:
            pass
        self._tick(1)

        t.stop()
        del t
