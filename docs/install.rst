Installation Guide
==================

.. contents::
   :local:

Device Support
--------------

wasp-os can run on multiple devices and, in time, will hopefully be ported to
many more.

In terms of deciding which device to buy we can suggest two criteria to help.

The first is simply based on aesthetic appeal. A watch is something that you
take everywhere and sits somewhere between clothing and jewellery. That means
it is important to choose a device that feels good on the wrist and
looks right when you glance at it. Aesthetics matter!

The second criteria is more subtle. In most cases, there is really not really
many important technical differences between the devices. They all use a Nordic
chipset and have the same display controller running a 240x240 panel. So the
second criteria is not technical, it is about community. The Pine64 PineTime is
unique among the devices supported by wasp-os because it is intended that the
watch be used to run a variety of different open source or free software
operating systems. By selling a watch with the intention that it be hacked
every which way from Sunday then we get a bigger stronger community focused on
the PineTime. There is a strong support forum, multiple different OS developers
(who share ideas and knowledge even if hacking on very different code bases)
combined with a reasonable set of hardware documentation.

There's definitely a lot of fun to be had buying something off-the-shelf and
hacking it to become something the manufacturer never intended. We know
this because we've done it! However the hackable devices are sold for
relatively short periods and may experience undocumented technical changes
between manufacturing runs. This makes it hard for a community to form
around any particular device.

Thus the second criteria it to think about your own needs and abilities.
If you want to enjoy the social and community aspects of open source
watch development then you should look very closely at the PineTime.

Pine64 PineTime (developer edition)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Pine64 PineTime is a square smart watch based on an nRF52832 SoC and
includes a 240x240 colour display with touch screen, a step counter and
a heart rate sensor.

The developer edition comes pre-programmed with a test firmware that
is used as part of the factory testing. Both the wasp-bootloader and
the main OS image can be installed onto a developer edition PineTime
using DaFlasher for Android. No tools are required to install using
DaFlasher.

Since the developer edition comes without the case glued shut it is
also possible to install the wasp-bootloader using an SWD programmer.

Colmi P8
~~~~~~~~

The Colmi P8 is an almost square smart watch based on an nRF52832 SoC
and includes a 240x240 colour display with touch screen, a step counter
and a heart rate sensor.

Both the wasp-bootloader and the main OS image can be installed onto a
P8 using DaFlasher for Android. No tools are required.

Installing wasp-bootloader using DaFlasher for Android
------------------------------------------------------

For all the DaFit family of smart watches (including the developer
edition of the Pine64 PineTime) the install instructions are the
same although it is important to ensure that both ``bootloader-daflasher.zip``
and ``micropython.zip`` match the device you are installing on. There are
no runtime checks.

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

Installing wasp-bootloader using an SWD programmer
--------------------------------------------------

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

Installing wasp-os using DaFlasher for Android
----------------------------------------------

To install the main firmware using DaFlasher for Android:

* Copy ``micropython.zip`` to your Android device and download DaFlasher
  if you do not already have it.
* Open the app and connect to the device (e.g. *PineDFU* if you have a
  PineTime).
* Click **Do DFU Update**.
* Click **Select DFU file** and select ``micropython.zip``.
* When the upload is complete the watch will reboot and launch the digital
  clock application.

Installing wasp-os using nRF Connect for Android
------------------------------------------------

To install the main firmware using nRF Connect for Android:

* Copy ``micropython.zip`` to your Android device and download nRF Connect
  for Android if you do not already have it.
* Connect to the device (e.g. *PineDFU* if you have a PineTime) using
  nRFConnect, click the DFU button and send ``micropython.zip`` to the device.
* When the upload is complete the watch will reboot and launch the digital
  clock application.

Installing wasp-os from a GNU/Linux workstation
-----------------------------------------------

To install the main firmware from a GNU/Linux workstation:

* Look up the MAC address for your watch (try: ``sudo hcitool lescan``\ ).
* Use ota-dfu to upload ``micropython.zip`` to the device. For example:
  ``tools/ota-dfu/dfu.py -z micropython.zip -a A0:B1:C2:D3:E3:F5 --legacy``
