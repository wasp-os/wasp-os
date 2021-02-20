.. _Roadmap:

Roadmap
=======

.. contents::
   :local:
   :depth: 1

N+1: "The future"
-----------------

For the N+1 release we describe features that are planned. Planned in this sense
means there is a developer willing to work on the feature but, for whatever reason,
the feature isn't yet at the top of anyone's list.

For the features planned for the next release of wasp-os then please look at
the versioned roadmap further through this document.

Bootloader
~~~~~~~~~~

* [ ] Stay in bootloader after battery run down
* [ ] Implement power off support (no splash screen)
* [ ] Colour boot logo support

Micropython
~~~~~~~~~~~

* [ ] Use SoftDevice sleep logic
* [ ] Fix BLE hangs
* [ ] Allow asynchronous control of the SPI chip select signals (this will
      allow for double buffered graphics updates)

0.5: Logging and sports mode
----------------------------

0.5 is planned to be a short sprint to develop sports and logging features
that provide deeper integration with the step counter.

Wasp-os
~~~~~~~

* [ ] Applications

  * [ ] Add a sports/activity app (a combined stopwatch and trip counter)
  * [ ] Extend the step counter app so vertical swipes can provide graphs
        of recent activity.
  * [ ] Add some basic distance estimation to the step counter application.

0.4: Integration, Fit and finish
--------------------------------

For 0.4 we focus on improving the watch/phone integration whilst also taking
steps to improve the general fit and finish.

Wasp-os
~~~~~~~

* [X] Watch/phone integration with GadgetBridge

  * [X] Set date/time
  * [X] Fully fledged wasp-os device class

* [X] Look and feel

  * [X] Add a simple theming approach
  * [X] Update icon for Music player
  * [X] Introduce fwd/back buttons to the music player
  * [X] Update icon for Alarm app
  * [X] Update art work for buttons in Confirmation view
  * [X] Reduce the size of the battery charge icon slightly (match bell)

* [X] Widgets

  * [X] Add a button widget
  * [X] Add a checkbox widget
  * [X] Add a spinner widget

* [X] Applications

  * [X] Introduce an analog watch face
  * [X] Add a configuration tool to enable disable applications

* [X] Documentation

  * [X] Describe how to upload pre-compiled modules
  * [X] Document the binary releases

0.3 (a.k.a. M3): Smartwatch
---------------------------

At M3 we start to build out full fitness tracking and notification
functionality.

Reloader
~~~~~~~~

* [X] Pre-flash image verification
* [X] Post-flash image verification
* [X] Board identity check
* [X] UICR update support
* [X] Improve linker map (everything except linker table at +256K)
* [X] mcuboot

  * [X] Reconfigurable entry point (allow reloader to run from mcuboot)
  * [X] Allow reloader to install mcuboot and flash app (from wasp-bootloader)
  * [X] Allow reloader to install wasp-os (from mcuboot)

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

* [X] Automatically enter SPI flash power saving mode

* [X] Documentation

  * [X] Contributors guide (and code of conduct)
  * [X] Debugging and troubleshooting guide
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
