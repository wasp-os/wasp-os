freeze('../..',
    (
        'boot.py',
        'demo.py',
        'drivers/battery.py',
        'drivers/signal.py',
        'drivers/st7789.py',
        'drivers/vibrator.py',
        'logo.py',
    ),
    opt=3
)
freeze('.', 'watch.py', opt=3)
