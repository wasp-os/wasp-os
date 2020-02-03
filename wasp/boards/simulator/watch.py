import time
def sleep_ms(ms):
    time.sleep(ms / 1000)
time.sleep_ms = sleep_ms

from machine import Pin
from machine import SPI

from drivers.st7789 import ST7789_SPI
from drivers.vibrator import Vibrator

class Backlight(object):
    def __init__(self, level=1):
        self.set(level)

    def set(self, level):
        print(f'BACKLIGHT: {level}')

class Display(ST7789_SPI):
    def __init__(self):
        spi = SPI(0)
        # Mode 3, maximum clock speed!
        spi.init(polarity=1, phase=1, baudrate=8000000)
    
        # Configure the display
        cs = Pin("DISP_CS", Pin.OUT, quiet=True)
        dc = Pin("DISP_DC", Pin.OUT, quiet=True)
        rst = Pin("DISP_RST", Pin.OUT, quiet=True)

        super().__init__(240, 240, spi, cs=cs, dc=dc, res=rst)

class RTC(object):
    def __init__(self):
        self.uptime = 0

    def update(self):
        now = time.time()
        if now == self.uptime:
            return False
        self.uptime = now
        return True

    def get_time(self):
        now = time.localtime()
        return (now[3], now[4], now[5])

    def uptime(self):
        return time.time

display = Display()
backlight = Backlight()
rtc = RTC()
vibrator = Vibrator(Pin('MOTOR', Pin.OUT, value=0), active_low=True)
button = Pin('BUTTON', Pin.IN, quiet=True)

