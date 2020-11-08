.. _Wasp-os Reference Manual:

Wasp-os Reference Manual
========================

.. contents::
    :local:

System
------

.. automodule:: wasp
   :members:

.. automodule:: watch

.. automodule:: draw565
   :members:

.. automodule:: icons
   :members:
   :undoc-members:

.. automodule:: fonts.clock
   :members:
   :undoc-members:

.. automodule:: fonts.sans24
   :members:

.. automodule:: logo
   :members:
   :undoc-members:

.. automodule:: widgets
   :members:

Device drivers
--------------

.. automodule:: drivers.battery
   :members:

.. automodule:: drivers.cst816s
   :members:

.. automodule:: drivers.nrf_rtc
   :members:

.. automodule:: drivers.signal
   :members:

.. automodule:: drivers.st7789
   :members:

.. automodule:: drivers.vibrator
   :members:

Applications
------------

.. automodule:: apps.clock
   :members:
   :undoc-members:

.. automodule:: apps.flashlight
   :members:
   :undoc-members:

.. automodule:: apps.launcher
   :members:
   :undoc-members:

.. automodule:: apps.pager
   :members:
   :undoc-members:

.. automodule:: apps.testapp
   :members:
   :undoc-members:

Bootloader
----------

The bootloader implements a couple of protocols that allow the bootloader
and payload to communicate during a reset or on handover from bootloader
to application.

GPREGRET protocol
~~~~~~~~~~~~~~~~~

``GPREGRET`` is a general purpose 8-bit retention register that is preserved
in all power states of the nRF52 (including System OFF mode when SRAM
content is destroyed).

It can be used by the application to request specific bootloader behaviours
during a reset:

================= ===== ======================================================
Name              Value Description
----------------- ----- ------------------------------------------------------
OTA_APPJUM         0xb1 Bootloader entered (without reset) from application.
OTA_RESET          0xa8 Enter OTA (Bluetooth) recovery mode
SERIAL_ONLY_RESET  0x4e Enter UART recovery mode (if applicable)
UF2_RESET          0x57 Enter USB recovery mode (if applicable)
FORCE_APP_BOOT     0x65 Force direct application boot (no splash screen)
================= ===== ======================================================

PNVRAM protocol
~~~~~~~~~~~~~~~

The pseudo non-volatile RAM is a small block of regular static RAM that,
once initialized, can be used to share information.

The PNVRAM starts at 0x200039c0 and is 32 bytes long.

========== ===================================================================
Address    Description
---------- -------------------------------------------------------------------
0x200039c0 Guard value. Must be set to 0x1abe11ed .
0x200039c4 Course grained RTC value (bootloader must preserve but can ignore).
0x200039c8 RTC millisecond counter (bootloader must increment this).
0x200039cc Reserved
0x200039d0 Reserved
0x200039d4 Reserved
0x200039d8 Reserved
0x200039cc Guard value. Must be set to 0x10adab1e .
========== ===================================================================

Note: *The PNVRAM protocol allows up to 28 bytes to be transfered (compared to
2 bytes via GPREGRET and GPREGRET2) but it is less versatile. For example
FORCE_APP_BOOT cannot be implmented using PNVRAM.*

The RTC millisecond counter is incremented whenever the bootloader is 
active (during splash screen or early UART recovery mode, during an
update). It can be consumed by the application to prevent the current
time being lost during an update.

Watchdog protocol
~~~~~~~~~~~~~~~~~

Form-factor devices such as smart watches and fitness trackers do not usually
have any hardware mechanism to allow the user to force a failed device into
bootloader mode. This makes them difficult to develop on because opening the
case to access a SWD or reset pins may compromise their waterproofing.

wasp-os uses a watchdog timer (WDT) combined with a single hardware button in
order to provide a robust mechanism to allow the user to force entry into a
over-the-air firmware recovery mode that allows the buggy application to be
replaced.

The software responsibilities to implement this are split between the
bootloader and the application, although the application responsibilities
are intentionally minimal.

The bootloader implements an over-the-air recovery mode, as well as handling
normal boot, where it's role is to display the splash screen.

Additionally the bootloader implements several watchdog related features
necessary for robust reboot handling:

1. The bootloader configures the watchdog prior to booting the main
   application. This is a simple, single channel reload request, watchdog
   with a 5 second timeout.

2. The bootloader checks the reset reason prior too booting the main
   application. If it detects a watchdog reset the bootloader switches
   automatically to DFU mode.

3. The bootlaoder initialized the pinmux allowing the hardware button
   state to be observed.

4. The bootloader monitors the hardware button and switches back to the main
   application when it is pressed.
    
From this list #1 and #2 are needed to ensure robust WDT handling whilst #3
and # 4 ensure the user can switch back to application from the device
itself if they ever accidentally trigger entry to recovery mode.

The application's role is to carefully pet the watchdog so that it will
trigger automatically if the hardware button is held down for five
seconds. Key points for application robustness include:

1. Unlike a normal watchdog we can be fairly reckless about where in the
   code we pet the dog. For example petting the dog from a timer interrupt
   is fine because we only need the dog to bark if the hardware button is
   pressed.

2. The routine to pet the dog is predicated on the hardware button not
   being pressed.

3. The routine to pet the dog is also predicated on the hardware button
   still being correctly configured.

To avoid mistakes the application should contain no subroutines that 
unconditionally pet the dog; they should all implement #2 and #3 from
the above list.

Note: *nRF52 microcontrollers implement a distributed pin-muxing
mechanism meaning most peripheral can acidentally "steal" a pin
if the pin is requested by the peripheral. This requires a fully
robust implementation of #3 to visit the PSEL registers of every
peripheral that can control pins. The code currently used in
wasp-os does not yet meet this criteria.*
