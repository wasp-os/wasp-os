.. _Roadmap:

Roadmap
=======

.. contents::
   :local:
   :depth: 1

0.4: Integration, Fit and finish
--------------------------------

For 0.4 we focus on improving the watch/phone integration whilst also taking steps
to improve the general fit and finish. In addition the reloader will be extended
to ensure we retain the capability to install wasp-os over-the-air on newer
PineTime models.

Bootloader
~~~~~~~~~~

* [ ] Stay in bootloader after battery run down
* [ ] Implement power off support (no splash screen)

Reloader
~~~~~~~~

* [ ] Board identity check
* [ ] UICR update support
* [ ] Improve linker map (everything except linker table at +256K)
* [ ] mcuboot

  * [ ] Reconfigurable entry point (allow reloader to run from mcuboot)
  * [ ] Allow reloader to install mcuboot and flash app (from wasp-bootloader)
  * [ ] Allow reloader to install wasp-os (from mcuboot)

Micropython
~~~~~~~~~~~

* [ ] Use SoftDevice sleep logic
* [ ] Automatically enter SPI flash power saving mode

Wasp-os
~~~~~~~

* [ ] Watch/phone integration

  * [ ] Music player support
  * [ ] Set date/time
  * [ ] Fully fledged wasp-os device class

0.3 (a.k.a. M3): Smartwatch
---------------------------

At M3 we start to build out full fitness tracking and notification
functionality.

Reloader
~~~~~~~~

* [X] Pre-flash image verification
* [X] Post-flash image verification

Wasp-os
~~~~~~~

* [X] Enable heart rate sensor

  * [X] HRS3300 driver
  * [X] HRS data post-processing
  * [X] Heart rate counter app

* [X] Notifications

  * [X] BLE notification protocol
  * [X] Notification popups
  * [X] Notification app (show notification history)
  * [X] Add (out-of-tree) Gadgetbridge support

* [X] Step counting

  * [X] BMA421 driver
  * [X] Step counter app

* [ ] Documentation

  * [X] Contributors guide (and code of conduct)
  * [ ] Debugging and troubleshooting guide
  * [X] Screenshots for bootloader and all applications
  * [X] Improve the install guide

* [X] Simulator

  * [X] Add a simple skin for better screenshots
  * [X] Full swipe detection (avoid keyboard)

0.2 (a.k.a. M2): Great developer experience
-------------------------------------------

The focus for M2 is to make development faster and easier by providing
a file system and file transfer code. This allows much faster
development cycles compared to full downloads of frozen modules.
Additionally support for multiple event-driven applications will be
added during M2 to further help developers by providing example
applications.

Bootloader
~~~~~~~~~~

* [X] OTA bootloader update
* [X] RTC time measurement whilst in bootloader

MicroPython
~~~~~~~~~~~

* [X] SPI FLASH driver
* [X] Enable LittleFS on SPI FLASH (at boot)
* [X] BLE file transfer

Wasp-os
~~~~~~~

* [X] Add dd/mm/yyyy support to RTC
* [X] Button driver (interrupt based)
* [X] Touch sensor driver
* [X] Event driven application framework
* [X] Stopwatch app
* [X] Settings app
* [X] PC-hosted simulation platform
* [X] Documentation

  * [X] Sphinx framework and integration with github.io
  * [X] Document bootloader protocols
  * [X] Application writer's guide
  * [X] Write full docstring documentation for all wasp-os components

* [X] Application Launcher
* [X] Debug notifications
* [X] Multi-colour RLE images

  * [X] Optimized "2-bit" RLE encoder and decoder
  * [X] Logarithmic RBG332 <-> RGB56516bit color space conversion

M1: Dumb watch feature parity
-----------------------------

The focus for M1 is to get wasp-os both to meet feature parity with a dumb
watch and to have a bootloader and watchdog strategy that is robust enough
to allow a PineTime case to be confidently glued shut.

Bootloader
~~~~~~~~~~

* [X] Basic board ports (PineTime, DS-D6, 96Boards Nitrogen)
* [X] OTA application update
* [X] Enable watchdog before starting the application
* [X] Splash screen
* [X] Ignore start button for first few seconds

MicroPython
~~~~~~~~~~~

* [X] Basic board ports (PineTime, DS-D6, 96Boards Nitrogen)
* [X] Long press reset (conditional feeding of the watchdog)

  * [X] Feed dog from REPL polling loop
  * [X] Feed dog from a tick interrupt

Wasp-os
~~~~~~~

* [X] Display driver

  * [X] Display initialization
  * [X] Bitmap blitting
  * [X] RLE coder and decoder
  * [X] Optimized RLE inner loops

* [X] Backlight driver
* [X] Button driver (polling)
* [X] Battery/charger driver
* [X] Simple clock and battery level application
* [X] Basic (WFI) power saving
* [X] Implement simple RTC for nrf52
