# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 Daniel Thompson

freeze('../..',
    (
        'drivers/battery.py',
        'drivers/signal.py',
        'drivers/st7789.py',
        'drivers/vibrator.py',
    ),
    opt=3
)
freeze('.', 'watch.py', opt=3)

