# Start measuring time (and feeding the watchdog) before *anything* else
from machine import RTCounter
from drivers.nrf_rtc import RTC
rtc = RTC(RTCounter(1, mode=RTCounter.PERIODIC))
rtc.counter.start()

import os
import time

import draw565

from machine import I2C
from machine import Pin
#from machine import Signal
from machine import SPI

from drivers.battery import Battery
from drivers.cst816s import CST816S
from drivers.signal import Signal
from drivers.st7789 import ST7789_SPI
from drivers.vibrator import Vibrator
from flash.flash_spi import FLASH

class Backlight(object):
    lo = Pin("BL_LO", Pin.OUT, value=0)
    mid = Pin("BL_MID", Pin.OUT, value=1)
    hi = Pin("BL_HI", Pin.OUT, value=1)

    def __init__(self, level=1):
        self.set(level)

    def set(self, level):
        hi = 1
        mid = 1
        lo = 1

        if level >= 3:
            hi = 0
        elif level == 2:
            mid = 0
        elif level == 1:
            lo = 0

        self.hi(hi)
        self.mid(mid)
        self.lo(lo)

# Setup the display (and manage the backlight)
backlight = Backlight(0)
spi = SPI(0)
spi.init(polarity=1, phase=1, baudrate=8000000)
display = ST7789_SPI(240, 240, spi,
        cs=Pin("DISP_CS", Pin.OUT),
        dc=Pin("DISP_DC", Pin.OUT),
        res=Pin("DISP_RST", Pin.OUT))
drawable = draw565.Draw565(display)

# Setup the last few bits and pieces
battery = Battery(
        Pin('BATTERY', Pin.IN),
        Signal(Pin('CHARGING', Pin.IN), invert=True),
        Signal(Pin('USB_PWR', Pin.IN), invert=True))
button = Pin('BUTTON', Pin.IN)
i2c = I2C(1, scl='I2C_SCL', sda='I2C_SDA')
touch = CST816S(i2c)
vibrator = Vibrator(Pin('MOTOR', Pin.OUT, value=0), active_low=True)

# Release flash from deep power-down
nor_cs = Pin('NOR_CS', Pin.OUT, value=1)
nor_cs(0)
spi.write('\xAB')
nor_cs(1)

# Mount the filesystem
flash = FLASH(spi, (Pin('NOR_CS', Pin.OUT, value=1),))
try:
    os.mount(flash, '/flash')
except AttributeError:
    # Format the filesystem (and provide a default version of main.py)
    os.VfsLfs2.mkfs(flash)
    os.mount(flash,'/flash')
    with open('/flash/main.py', 'w') as f:
        f.write('''\
import manager
wasp = manager.Manager(watch)
wasp.run()
''')

# Only change directory if the button is not pressed (this will
# allow us access to fix any problems with main.py)!
if not button.value():
    os.chdir('/flash')
    backlight.set(1)
else:
    display.poweroff()

