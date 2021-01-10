# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 Daniel Thompson

import wasp

# Adopt a basic all-orange theme
wasp.system.set_theme(
        b'\xff\x00'     # ble
        b'\xff\x00'     # scroll-indicator
        b'\xff\x00'     # battery
        b'\xff\x00'     # status-clock
        b'\xff\x00'     # notify-icon
        b'\xff\x00'     # bright
        b'\xbe\xe0'     # mid
        b'\xff\x00'     # ui
        b'\xff\x00'     # spot1
        b'\xff\x00'     # spot2
        b'\x00\x0f'     # contrast
    )

from gadgetbridge import *
wasp.system.schedule()
