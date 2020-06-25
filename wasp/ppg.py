# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 Daniel Thompson

"""Photoplethysmogram (PPG) Signal Processing
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Algorithms and signal processing primatives that can be used to convert
raw PPG signals into something useful.
"""

import array
import micropython

@micropython.viper
def _compare(d1, d2, count: int, shift: int) -> int:
    """Compare two sequences of (signed) bytes and quantify how dissimilar
    they are.
    """
    p1 = ptr8(d1)
    p2 = ptr8(d2)

    e = 0
    for i in range(count):
        s1 = int(p1[i])
        if s1 > 127:
            s1 -= 256

        s2 = int(p2[i])
        if s2 > 127:
            s2 -= 256

        d = s1 - s2
        e += d*d
    return e

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

class PPG():
    """
    """

    def __init__(self, spl):
        self._offset = spl
        self.data = array.array('b')

        self._hpf = Biquad(0.87033078, -1.74066156, 0.87033078,
                                       -1.72377617, 0.75754694)
        self._agc = PTAGC(20, 0.971, 2)
        self._lpf = Biquad(0.11595249, 0.23190498, 0.11595249,
                                      -0.72168143, 0.18549138)

    def preprocess(self, spl):
        """Preprocess a PPG sample.

        Must be called at 24Hz for accurate heart rate calculations.
        """
        spl -= self._offset
        spl = self._hpf.step(spl)
        spl = self._agc.step(spl)
        spl = self._lpf.step(spl)
        spl = int(spl)

        self.data.append(spl)
        return spl

    def _get_heart_rate(self):
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

        data = memoryview(self.data)

        # Search initially from ~210 to 30 bpm
        t0 = trough(data, 7, 48)
        if t0 < 0:
            return None

        # Check the second cycle ...
        t1 = t0 * 2
        t1 = trough(data, t1 - 5, t1 + 5)
        if t1 < 0:
            return None

        # ... and the third
        t2 = (t1 * 3) // 2
        t2 = trough(data, t2 - 5, t2 + 4)
        if t2 < 0:
            return None

        # If we can find a fourth cycle then use that for the extra
        # precision otherwise report whatever we've found
        t3 = (t2 * 4) // 3
        t3 = trough(data, t3 - 4, t3 + 4)
        if t3 < 0:
            return (60 * 24 * 3) // t2
        return (60 * 24 * 4) // t3

    def get_heart_rate(self):
        if len(self.data) < 200:
            return None

        hr = self._get_heart_rate()

        # Clear out the accumulated data
        self.data = array.array('b')

        return hr
