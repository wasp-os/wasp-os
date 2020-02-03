from machine import Pin
from machine import RTCounter
#from machine import Signal
from machine import SPI

from drivers.battery import Battery
from drivers.nrf_rtc import RTC
from drivers.signal import Signal
from drivers.st7789 import ST7789_SPI
from drivers.vibrator import Vibrator

class Display(ST7789_SPI):
    def __init__(self):
        spi = SPI(0)
        # Mode 3, maximum clock speed!
        spi.init(polarity=1, phase=1, baudrate=8000000)

        # Configure the display
        cs = Pin("DISP_CS", Pin.OUT)
        dc = Pin("DISP_DC", Pin.OUT)
        rst = Pin("DISP_RST", Pin.OUT)

        super().__init__(240, 240, spi, cs=cs, dc=dc, res=rst)

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

backlight = Backlight(0)
display = Display()
backlight.set(1)

# Start measuring time (and feeding the watchdog)
rtc = RTC(RTCounter(1, mode=RTCounter.PERIODIC))
rtc.counter.start()

battery = Battery(
        Pin('BATTERY', Pin.IN),
        Signal(Pin('CHARGING', Pin.IN), invert=True),
        Signal(Pin('USB_PWR', Pin.IN), invert=True))
vibrator = Vibrator(Pin('MOTOR', Pin.OUT, value=0), active_low=True)
button = Pin('BUTTON', Pin.IN)
