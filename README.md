Watch Application System in Python
==================================

Despite the grand ambitions of the name, currently this repo simply 
combines a bootloader, derived from the Adafruit NRF52 bootloader, with 
MicroPython. Both have been ported to Pine64 PineTime and the Desay
DS-D6 fitness band.

Try:

~~~
make submodules
make softdevice
make -j `nproc` all
make flash
~~~

Then use nRFConnect (for Android) to program micropython.zip.

At the end of this process your watch may *look* dead but, if it works, 
you will be able to use the Nordic UART Service to access the 
MicroPython REPL.

Drivers are, for the most part, an exercise for the reader but
there is a proof-of-concept display driver. To experiment try:

~~~
import pinetime, time
tft = pinetime.st7789()
tft.white()
time.sleep(2)
tft.black()
~~~
