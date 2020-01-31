import time
def sleep_ms(ms):
    time.sleep(ms / 1000)
time.sleep_ms = sleep_ms

from machine import Pin
from machine import SPI

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

display = Display()
vibrator = Vibrator(Pin('MOTOR', Pin.OUT, value=0), active_low=True)
