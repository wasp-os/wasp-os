# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 Daniel Thompson

import time
def sleep_ms(ms):
    time.sleep(ms / 1000)
time.sleep_ms = sleep_ms

class Pin():
    def value(v=None):
        pass

button = Pin()
