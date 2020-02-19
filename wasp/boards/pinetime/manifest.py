freeze('.', 'watch.py', opt=3)
freeze('../..',
    (
        'boot.py',
        'clock.py',
        'demo.py',
        'draw565.py',
        'drivers/battery.py',
        'drivers/nrf_rtc.py',
        'drivers/signal.py',
        'drivers/st7789.py',
        'drivers/vibrator.py',
        'fonts/clock.py',
        'fonts/sans24.py',
        'icons.py',
        'logo.py',
        'manager.py',
        'shell.py',
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
