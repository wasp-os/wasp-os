Installation Guide
==================

.. contents::
   :local:

.. _Building wasp-os from source:

Building wasp-os from source
----------------------------

Building wasp-os and launching the wasp-os simulator requires Python 3.6
(or later) and the following python modules: click, numpy, pexpect, PIL
(or Pillow), pyserial, pysdl2.

On Debian Buster the required python modules can be obtained using the
following commands:

.. code-block:: sh

    sudo apt install \
      git build-essential libsdl2-2.0.0 python3-click python3-numpy \
      python3-pexpect python3-pil python3-pip python3-serial
    pip3 install --user pysdl2

Additionally if you wish to regenerate the documentation you will require
a complete sphinx toolchain:

.. code-block:: sh

    sudo apt install sphinx graphviz python3-recommonmark

Alternatively, if your operating system does not package some or any of
the aforementioned Python modules that were included in the previous
command, you can install all of them with pip instead. Make sure to 
adapt the following command appropriately:

.. code-block:: sh

    pip3 install --user click numpy pexpect Pillow pyserial pysdl2

You will also need a toolchain for the Arm Cortex-M4. wasp-os is developed and
tested using the `GNU-RM toolchain
<https://developer.arm.com/tools-and-software/open-source-software/developer-tools/gnu-toolchain/gnu-rm>`_
(9-2019-q4) from Arm.

.. note::

    There are known problems with toolchains older than gcc-7.3 when
    link time optimization is enabled during the MicroPython build
    (and LTO is enabled by default).

Fetch the code from
`https://github.com/daniel-thompson/wasp-os <https://github.com/daniel-thompson/wasp-os>`_ :

.. code-block:: sh

   git clone https://github.com/daniel-thompson/wasp-os
   cd wasp-os
   make submodules
   make softdevice

To build the firmware select the command appropriate for your board from the
list below:

.. code-block:: sh

   make -j `nproc` BOARD=pinetime all
   make -j `nproc` BOARD=k9 all
   make -j `nproc` BOARD=p8 all

To rebuild the documentation try:

.. code-block:: sh

   make docs

Device Support
--------------

wasp-os can run on multiple devices and, in time, will hopefully be ported to
many more.

In terms of deciding which device to buy we can suggest two criteria to help.

The first is simply based on aesthetic appeal. A watch is something that you
take everywhere and sits somewhere between clothing and jewellery. That means
it is important to choose a device that feels good on the wrist and
looks right when you glance at it. Aesthetics matter!

The second criteria is more subtle. In most cases, there is not really many
important technical differences between the devices. They all use a Nordic
chipset and have the same display controller running a 240x240 panel. So the
second criteria is not technical, it is about community. The Pine64 PineTime is
unique among the devices supported by wasp-os because it is intended that the
watch be used to run a variety of different open source or free software
operating systems. By manufacturing a watch with the intention that it be
hacked every which way from Sunday then we get a bigger stronger community
focused on the PineTime. There is a vibrant support forum, multiple different
OS developers (who share ideas and knowledge even if hacking on very different
code bases) combined with a `near complete set of hardware documentation
<https://wiki.pine64.org/index.php/PineTime>`_.

There's definitely a lot of fun to be had buying something off-the-shelf and
hacking it to become something the manufacturer never intended. We know this
because we've done it! However there is also enormous benefit from
participating in a community, especially if you enjoy working with or learning
from other developers. Devices that can repurposed to run wasp-os are often
only sold for short periods and may experience undocumented technical changes
between manufacturing runs that can cause compatibility problems. This makes it
hard for a large community to form around these devices.

Thus the second criteria it to think about your own needs and abilities.  If
you want to enjoy the social and community aspects of working together on open
source watch development then you should look very closely at the PineTime.

Pine64 PineTime (developer edition)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

`Pine64 PineTime <https://www.pine64.org/pinetime/>`_ is a square smart watch
based on an nRF52832 SoC and includes a 240x240 colour display with touch
screen, a step counter and a heart rate sensor.

The `developer edition <https://store.pine64.org/?product=pinetime-dev-kit>`_
comes pre-programmed with a test firmware that is used as part of the factory
testing.  DaFlasher for Android can be used to install both the 
:ref:`wasp-bootloader<Bootloader DaFlasher>` and the
:ref:`main OS image<Main OS DaFlasher>`. No tools or disassembly is required
to install using DaFlasher.

Since the developer edition comes without the case glued shut it is
also possible to install the wasp-bootloader using an SWD programmer.

The wasp-os simulator
~~~~~~~~~~~~~~~~~~~~~

The simulator allows you to run wasp-os programs using the Python
interpreter included with your host operating system. The simulator
provides a 240x240 colour display together with a touch screen and a
physical button, all of which appears as a window on your host computer.

The simulator has large quantities of memory and, whilst useful for
exploring wasp-os and testing your programs are syntactically correct
it is not a substitute for testing on real hardware. See
:ref:`Testing on the simulator` for more details on how to use the simulator.

To launch the simulator try:

.. code-block:: sh

    make sim

Senbono K9
~~~~~~~~~~

The Senbono K9 is a circular smart watch based on an nRF52832 SoC and includes
with a square 240x240 colour with a touch screen, a step counter and a heart
rate sensor.

The wasp-os port for Senbono K9 does not, at this point, include a driver for
the touch screen because the protocol has not yet been reverse engineered. The
touch screen enumerates via I2C at address 70d (or 0x46) and the interrupt can
be used to detect touch screen activity but the touch coordinates cannot be
read from the hardware. Currently the touch screen can only act as a
multi-function button and can be used to cycle through the quick ring and
display notifications. This makes the device usable but not fully featured.

Note also that the to conceal the square display within the circular face this
device has a heavily tinted filter over the display. This improves the look of
the device but also significantly dims the backlight making it difficult to
read the display in strong sunlight.

DaFlasher for Android can be used to install both the 
:ref:`wasp-bootloader<Bootloader DaFlasher>` and the
:ref:`main OS image<Main OS DaFlasher>`. No tools or disassembly is required.

Colmi P8
~~~~~~~~

The `Colmi P8 <https://www.colmi.com/products/p8-smartwatch>`_ is an almost
square smart watch based on an nRF52832 SoC and includes a 240x240 colour
display with touch screen, a step counter and a heart rate sensor.

DaFlasher for Android can be used to install both the 
:ref:`wasp-bootloader<Bootloader DaFlasher>` and the
:ref:`main OS image<Main OS DaFlasher>`. No tools or disassembly is required.

Installing wasp-bootloader
--------------------------

.. _Bootloader DaFlasher:

DaFlasher for Android
~~~~~~~~~~~~~~~~~~~~~

To install the bootloader using DaFlasher for Android:

* Download and install
  `DaFlasher <https://play.google.com/store/apps/details?id=com.atcnetz.paatc.patc>`_
  and copy the DaFlasher bootloaders to your Android device. You will need
  `DaFitBootloader23Hacked.bin <https://github.com/atc1441/DaFlasherFiles/blob/master/DaFitBootloader23Hacked.bin>`_ and
  `FitBootloaderDFU2.0.1.zip <https://github.com/atc1441/DaFlasherFiles/blob/master/FitBootloaderDFU2.0.1.zip>`_.
* Copy ``bootloader-daflasher.zip`` (see :ref:`Building wasp-os from source`
  above) to your Android device.
* Open the app and connect to the device (e.g. *Y7S* if you have a developer
  edition PineTime).
* Read the disclaimer carefully, then click **Ok**.
  PineTime).
* Click **Select file** and choose ``DaFitBootloader23Hacked.bin``, then wait
  for the payload to be transferred and for the install process to complete
  on the watch (leaving three coloured squares on the display).
* Press the Back button to return to the scanner and connect to the device.
  The device name will have changed to *ATCdfu*.
* Click **Do DFU Update**.
* Click **Select DFU file** and select ``FitBootloaderDFU2.0.1.zip``, then wait
  for the payload to transfer and the update to take place. The watch should
  be showing a single red square which is captioned *ATCnetz.de*.
* Click **Select DFU file** again and select
  ``bootloader-daflasher.zip``. Once the update is complete the watch will
  show the wasp-os logo and some additional on-screen prompt.

It is important to ensure that both ``bootloader-daflasher.zip``
and ``micropython.zip`` match the device you are installing for. There are
no runtime compatibility checks.

An end-to-end video of the above process (and the final install of wasp-
os) is also available:

.. image:: https://img.youtube.com/vi/VJoDtMy-4pk/0.jpg
   :target: https://www.youtube.com/watch?v=VJoDtMy-4pk
   :alt: Installing MicroPython on a Colmi P8 smart watch using DaFlasher
   :width: 320
   :height: 240

`Installing MicroPython on a Colmi P8 smart watch using DaFlasher <https://www.youtube.com/watch?v=VJoDtMy-4pk>`_

.. warning::

    The first step cannot be reversed. Once ``DaFitBootloader23Hacked.bin``
    has been installed the factory firmware will be permanently removed
    from the device.

    Although it is not possible to restore the factory firmware it is
    possible to switch back to Softdevice 5.0.1 and/or Softdevice 2.0.1
    on order to run alternative firmwares such as
    `ATCwatch <https://github.com/atc1441/ATCwatch>`_. The zip updates
    in `DaFlasherFiles <https://github.com/atc1441/DaFlasherFiles>`_ cannot
    be applied directly but we can return to the DaFlasher bootloaders
    by installing
    `DS-D6-adafruit-back-to-desay-sd132v201.zip <https://github.com/fanoush/ds-d6/blob/master/micropython/DS-D6-adafruit-back-to-desay-sd132v201.zip>`_
    followed by
    `ATCdfuFromSD2toSD5.zip <https://github.com/atc1441/DaFlasherFiles/blob/master/ATCdfuFromSD2toSD5.zip>`_

Using an SWD programmer
~~~~~~~~~~~~~~~~~~~~~~~

There are many different SWD programmers that can be used to install
wasp-bootloader. Use the
`PineTime SWD programming guide <https://wiki.pine64.org/index.php/Reprogramming_the_PineTime>`_
to lookup the specific instructions for your programmer.

Use the SWD programmer to install ``bootloader.hex`` to the device.
This file is an Intel HEX file containing both the bootloader and the Nordic
SoftDevice. Once the bootloader is installed the watch will boot, display a
logo and wait for a OTA update.

.. note::

    If you have a new device then it may have been delivered with flash
    protection enabled. You must disable the flash protection before trying to
    program it.

    Be careful to disconnect cleanly from the debug software since just pulling
    out the SWD cable will mean the nRF52 will still believe it is being
    debugged (which harms battery life because the device won't properly enter
    deep sleep states).

Installing wasp-os
------------------

.. _Main OS DaFlasher:

DaFlasher for Android
~~~~~~~~~~~~~~~~~~~~~

To install the main firmware using DaFlasher for Android:

* Copy ``micropython.zip`` (see :ref:`Building wasp-os from source`) to 
  your Android device and download
  `DaFlasher <https://play.google.com/store/apps/details?id=com.atcnetz.paatc.patc>`_
  if you do not already have it.
* Open the app and connect to the device (e.g. *PineDFU* if you have a
  PineTime).
* Click **Do DFU Update**.
* Click **Select DFU file** and select ``micropython.zip``.
* When the upload is complete the watch will reboot and launch the digital
  clock application.

nRF Connect for Android
~~~~~~~~~~~~~~~~~~~~~~~

To install the main firmware using nRF Connect for Android:

* Copy ``micropython.zip`` (see :ref:`Building wasp-os from source`) to 
  your Android device and download
  `nRF Connect <https://play.google.com/store/apps/details?id=no.nordicsemi.android.mcp>`_
  for Android if you do not already have it.
* Connect to the device (e.g. *PineDFU* if you have a PineTime) using
  nRFConnect, click the DFU button and send ``micropython.zip`` to the device.
* When the upload is complete the watch will reboot and launch the digital
  clock application.

wasptool for GNU/Linux
~~~~~~~~~~~~~~~~~~~~~~

To install the main firmware from a GNU/Linux workstation:

* Look up the MAC address for your watch (try: ``sudo hcitool lescan``\ ).
* Use ota-dfu to upload ``micropython.zip`` (see
  :ref:`Building wasp-os from source`) to the device. For example:
  ``tools/ota-dfu/dfu.py -z micropython.zip -a A0:B1:C2:D3:E3:F5 --legacy``
