# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 Daniel Thompson

from machine import RTCounter as RTC

# Start measuring time (and feeding the watchdog)
rtc = RTC(1, mode=RTC.PERIODIC)
rtc.start()
