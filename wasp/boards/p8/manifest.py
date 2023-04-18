# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 Daniel Thompson

import os, sys

sys.path.append(os.path.dirname(os.getcwd()))
import manifest_240x240
import manifest_user_apps

freeze('.', 'watch.py', opt=3)
freeze('../..', manifest_240x240.manifest + manifest_user_apps.manifest +
    (
        'boot.py',
        'draw565.py',
        'drivers/bma421.py',
        'drivers/battery.py',
        'drivers/cst816s.py',
        'drivers/hrs3300.py',
        'drivers/nrf_rtc.py',
        'drivers/signal.py',
        'drivers/st7789.py',
        'drivers/vibrator.py',
        'gadgetbridge.py',
        'ppg.py',
        'shell.py',
        'wasp.py',
    ),
    opt=3
)
freeze('../../drivers/flash',
    (
        'bdevice.py',
        'flash/flash_spi.py'
    ), opt=3
)
