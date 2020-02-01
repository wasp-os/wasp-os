freeze('../..',
    (
        'demo.py',
        'drivers/battery.py',
        'drivers/signal.py',
        'drivers/vibrator.py',
    ),
    opt=3
)
freeze('.', 'watch.py', opt=3)

