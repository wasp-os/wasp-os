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

class Battery(object):
    def __init__(self):
        self.voltage = 3.9
        self.step = -0.01
        self.powered = False

    def charging(self):
        self.voltage_mv()
        return self.powered

    def power(self):
        self.voltage_mv()
        return self.powered

    def voltage_mv(self):
        if self.voltage > 4:
            self.step = -0.005
            self.powered = False
        elif self.voltage < 3.4:
            self.step = 0.01
            self.powered = True
        self.voltage += self.step

        return int(self.voltage * 1000)

    def level(self):
        mv = self.voltage_mv()
        level = ((19 * mv) // 100) - 660
        if level > 100:
            return 100
        if level < 0:
            return 0
        return level

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
battery = Battery()
rtc = RTC()
vibrator = Vibrator(Pin('MOTOR', Pin.OUT, value=0), active_low=True)
button = Pin('BUTTON', Pin.IN, quiet=True)

