# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 Daniel Thompson

import wasp
import array
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

def _compare(d1, d2, count, shift):
    e = 0
    for i in range(count):
        d = d1[i] - d2[i]
        e += d*d
    return e

def compare(d, shift):
    return _compare(d[shift:], d[:-shift], len(d)-shift, shift)

def trough(d, mn, mx):
    z2 = compare(d, mn-2)
    z1 = compare(d, mn-1)
    for i in range(mn, mx+1):
        z = compare(d, i)
        if z2 > z1 and z1 < z:
            return i
        z2 = z1
        z1 = z

    return -1

def get_hrs(d):
    din = memoryview(d)

    # Search initially from ~210 to 30 bpm
    t0 = trough(din, 7, 48)
    if t0 < 0:
        return None

    # Check the second cycle ...
    t1 = t0 * 2
    t1 = trough(din, t1 - 5, t1 + 5)
    if t1 < 0:
        return None

    # ... and the third
    t2 = (t1 * 3) // 2
    t2 = trough(din, t2 - 5, t2 + 4)
    if t2 < 0:
        return None

    # If we can find a fourth cycle then use that for the extra
    # precision otherwise report whatever we've found
    t3 = (t2 * 4) // 3
    t3 = trough(din, t3 - 4, t3 + 4)
    if t3 < 0:
        return (60 * 24 * 3) // t2
    return (60 * 24 * 4) // t3

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

        self._hpf = Biquad(0.87033078, -1.74066156, 0.87033078, -1.72377617, 0.75754694)
        self._agc = PTAGC(20, 0.971, 2)
        self._lpf = Biquad(0.11595249, 0.23190498, 0.11595249, -0.72168143, 0.18549138)

        self._x = 0
        self._offset = wasp.watch.hrs.read_hrs()

        self._hrdata = array.array('b')

        wasp.system.request_tick(1000 // 8)

    def background(self):
        wasp.watch.hrs.disable()
        del self._hpf
        del self._agc
        del self._lpf

    def _subtick(self, ticks):
        """Notify the application that its periodic tick is due."""
        draw = wasp.watch.drawable

        spl = wasp.watch.hrs.read_hrs()
        spl -= self._offset
        spl = self._hpf.step(spl)
        spl = self._agc.step(spl)
        spl = self._lpf.step(spl)
        spl = int(spl)

        self._hrdata.append(spl)
        if len(self._hrdata) >= 240:
            draw.string('{} bpm'.format(get_hrs(self._hrdata)), 0, 6, width=240)
            del self._hrdata
            self._hrdata = array.array('b')

        color = 0xffc0

        # If the maths goes wrong lets show it in the chart!
        if spl > 100 or spl < -100:
            color = 0xffff
        if spl > 104 or spl < -104:
            spl = 0
        spl += 104

        x = self._x
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
