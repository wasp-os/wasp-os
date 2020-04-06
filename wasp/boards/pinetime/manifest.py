# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 Daniel Thompson

freeze('.', 'watch.py', opt=3)
freeze('../..',
    (
        'apps/clock.py',
        'apps/flashlight.py',
        'apps/launcher.py',
        'apps/testapp.py',
        'boot.py',
        'demo.py',
        'draw565.py',
        'drivers/battery.py',
        'drivers/cst816s.py',
        'drivers/nrf_rtc.py',
        'drivers/signal.py',
        'drivers/st7789.py',
        'drivers/vibrator.py',
        'fonts/clock.py',
        'fonts/sans24.py',
        'icons.py',
        'logo.py',
        'shell.py',
        'wasp.py',
        'widgets.py',
    ),
    opt=3
)
freeze('../../drivers/flash',
    (
        'bdevice.py',
        'flash/flash_spi.py'
    ), opt=3
)
