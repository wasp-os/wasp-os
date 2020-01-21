from machine import Pin
from machine import SPI

from drivers.st7789 import ST7789

def st7789():
    spi = SPI(0)
    # Mode 3, maximum clock speed!
    spi.init(polarity=1, phase=1, baudrate=8000000)
    
    # Extra pins required by the driver
    cs = Pin("SPI_SS2", Pin.OUT)
    dc = Pin("P18", Pin.OUT)
    rst = Pin("P26", Pin.OUT)
    bl = Pin("P22", Pin.OUT)

    tft = ST7789(spi, cs=cs, dc=dc, rst=rst)
    bl.off() # active low
    return tft
