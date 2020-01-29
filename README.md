Watch Application System in Python
==================================

Currently WASP is primarily useful as a pre-packaged MicroPython
development environment for PineTime. Whilst there are plans to grow 
it into a smart watch runtime for Pine64 PineTime and the Desay
DS-D6 fitness  tracker this goal has yet to be achieved.

WASP includes a robust bootloader based on the Adafruit NRF52
Bootloader. It has been extended to make it robust for development on
form-factor devices without a reset button, power switch, SWD debugger
or UART. This allows us to confidently develop on sealed devices relying
only on BLE for updates.

Building from a git clone
-------------------------

~~~
make submodules
make softdevice
make -j `nproc` BOARD=pinetime all
~~~

Installing
----------

Note: *If you have a new PineTime then it will have been delivered with
flash protection enabled. You must disable the flash protection before
trying to program it.*

* Use an SWD programmer to install `bootloader.hex` to the PineTime.
  This file is an Intel HEX file containing both the bootloader and
  the Nordic SoftDevice. Be careful to disconnect cleanly from the
  debug software since just pulling out the SWD cable will mean the
  nRF52 will still believe it is being debugged.
* Copy `micropython.zip` to your Android device and download nRF Connect
  for Android if you do not already have it.
* In nRF Connect, choose settings and reduce the DFU packet count from
  10 to 4.
* Connect to PineDFU using nRFConnect, click the DFU button and send
  `micropython.zip` to the device.

At the end of this process your watch you will see a couple of splash
screens (bootloader shows a small Pine64 logo, MicroPython shows are
larger one). Once the second splash screen appears you will be able to 
use the Nordic UART Service to access the MicroPython REPL.

Drivers are still in development, see the [TODO list](todo.md) for
current status. In the mean time try the following and then take
a look at the `wasp/` directory to see how it works:

~~~
import demo
demo.run()
~~~
