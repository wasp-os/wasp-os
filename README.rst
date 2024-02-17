Watch Application System in Python
==================================

Introduction
------------

Wasp-os is a firmware for smart watches that are based on the nRF52 family of
microcontrollers, and especially for hacker friendly watches such as the Pine64
PineTime. Wasp-os features full heart rate monitoring and step counting support
together with multiple clock faces, a stopwatch, an alarm clock, a countdown
timer, a calculator and lots of other games and utilities. All of this, and
still with access to the MicroPython REPL for interactive tweaking, development
and testing.

Wasp-os comes fully integrated with a robust bootloader based on the Adafruit
NRF52 Bootloader. The bootloader has been extended to make it robust for
development on form-factor devices without a reset button, power switch, SWD
debugger or UART. This allows us to confidently develop on sealed devices
relying on Bluetooth Low Energy for over-the-air updates.

Documentation
-------------

Wasp-os is has `extensive documentation <https://wasp-os.readthedocs.io>`_
which includes a detailed `Application Writer's Guide
<https://wasp-os.readthedocs.io/en/latest/appguide.html>`_ to help you
get started coding for wasp-os as quickly as possible.

Getting Started
---------------

Wasp-os can be installed without using any tools or disassembly onto the
following devices:

 * Pine64 PineTime
 * Colmi P8
 * Senbono K9

Use the
`Installation Guide <https://wasp-os.readthedocs.io/en/latest/install.html>`_
to learn how to build and install wasp-os on these devices.

At the end of the install process your watch will show the time (03:00)
together with a date and a battery meter. When the watch goes into power
saving mode you can use the button to wake it again.

At this point you will also be able to use the Nordic UART Service to
access the MicroPython REPL. You can use ``tools/wasptool --console``
to access the MicroPython REPL.

To set the time and restart the main application:

.. code-block:: python

   ^C
   watch.rtc.set_localtime((yyyy, mm, dd, HH, MM, SS))
   wasp.system.run()

Or, if you have a suitable GNU/Linux workstation, just use:

.. code-block:: sh

   ./tools/wasptool --rtc

which can run these commands automatically.

As mentioned above there are many drivers and features still to be
developed, see the :ref:`Roadmap` for current status.

Community
---------

The wasp-os community is centred around the
`github project <https://github.com/wasp-os/wasp-os>`_ and is
supplemented with instant messaging in the
`#wasp-os:matrix.org <https://matrix.to/#/#wasp-os:matrix.org>`_
channel. If you do not have a preferred Matrix chat client then we recommend
trying out the
`Element web client <https://app.element.io/#/room/#wasp-os:matrix.org>`_
Follow the element link and, if you do not already have a matrix account,
register yourself. That should be enough to get you chatting!

Alternatively, if you prefer to use IRC then, for all
`the usual reasons <https://xkcd.com/1782/>`_ the Matrix channel is also
bridged to the #wasp-os IRC channel at libera.chat.

Videos
------

.. list-table::

   * - .. figure:: res/thumbnail-nps8Kd2qPzs.jpg
          :target: https://www.youtube.com/watch?v=nps8Kd2qPzs
          :alt: wasp-os: A tour of the new applications for wasp-os
          :width: 95%

          `A tour of the new applications for wasp-os <https://www.youtube.com/watch?v=nps8Kd2qPzs>`_

     - .. figure:: https://img.youtube.com/vi/lIo2-djNR48/0.jpg
          :target: https://www.youtube.com/watch?v=lIo2-djNR48
          :alt: wasp-os: Open source heart rate monitoring for Pine64 PineTime
          :width: 95%

          `Open source heart rate monitoring for Pine64 PineTime <https://www.youtube.com/watch?v=lIo2-djNR48>`_

   * - .. figure:: https://img.youtube.com/vi/YktiGUSRJB4/0.jpg
          :target: https://www.youtube.com/watch?v=YktiGUSRJB4
          :alt: An M2 pre-release running on Pine64 PineTime
          :width: 95%

          `An M2 pre-release running on Pine64 PineTime <https://www.youtube.com/watch?v=YktiGUSRJB4>`_

     - .. figure:: https://img.youtube.com/vi/tuk9Nmr3Jo8/0.jpg
          :target: https://www.youtube.com/watch?v=tuk9Nmr3Jo8
          :alt: How to develop wasp-os python applications on a Pine64 PineTime
          :width: 95%

          `How to develop wasp-os python applications on a Pine64 PineTime <https://www.youtube.com/watch?v=tuk9Nmr3Jo8>`_

   * - .. figure:: https://img.youtube.com/vi/kf1VHj587Mc/0.jpg
          :target: https://www.youtube.com/watch?v=kf1VHj587Mc
          :alt: Developing for Pine64 PineTime using wasp-os and MicroPython
          :width: 95%

          `Developing for Pine64 PineTime using wasp-os and MicroPython <https://www.youtube.com/watch?v=kf1VHj587Mc>`_

     -

Custom builds
-------------

Wasp-os is designed to allow users to easily create their own custom builds. Simply modify the wasp.toml file
to include your favorite apps and watch faces. See the docs for more information on how to build wasp-os.

Screenshots
-----------

(An older version of) the digital clock application running on a Pine64
PineTime:

.. image:: res/clock_app.jpg
   :alt: wasp-os digital clock app running on PineTime
   :width: 233

Screenshots of the available applications running on the wasp-os
simulator:

.. image:: res/Bootloader.png
   :alt: Bootloader splash screen overlaid on the simulator watch art
   :width: 179

Watch faces:

.. image:: res/screenshots/ClockApp.png
   :alt: Digital clock application running on the wasp-os simulator
   :width: 179

.. image:: res/screenshots/WeekClockApp.png
   :alt: Digital clock application with week day running on the wasp-os simulator
   :width: 179

.. image:: res/screenshots/ChronoApp.png
   :alt: Analogue clock application running in the wasp-os simulator
   :width: 179

.. image:: res/screenshots/DualClockApp.png
   :alt: An other clock application running in the wasp-os simulator
   :width: 179

.. image:: res/screenshots/FibonacciClockApp.png
   :alt: Fibonacci clock application running in the wasp-os simulator
   :width: 179

.. image:: res/screenshots/WordClockApp.png
   :alt: Shows a time as words in the wasp-os simulator
   :width: 179

.. image:: res/screenshots/ResistorClockApp.png
   :alt: Resistor colour code clock application running in the wasp-os simulator
   :width: 179

Games:

.. image:: res/screenshots/Play2048App.png
   :alt: Let's play the 2048 game (in the wasp-os simulator)
   :width: 179

.. image:: res/screenshots/GameOfLifeApp.png
   :alt: Game of Life running in the wasp-os simulator
   :width: 179

.. image:: res/screenshots/SnakeApp.png
   :alt: Snake Game running in the wasp-os simulator
   :width: 179

.. image:: res/screenshots/Puzzle15App.png
   :alt: 15 Puzzle running in the wasp-os simulator
   :width: 179

.. image:: res/screenshots/FourInARowApp.png
   :alt: Four In A Row running in the wasp-os simulator
   :width: 179

Time management apps:

.. image:: res/screenshots/AlarmApp.png
   :alt: Alarm clock application running in the wasp-os simulator
   :width: 179

.. image:: res/screenshots/StopwatchApp.png
   :alt: Stop watch application running on the wasp-os simulator
   :width: 179

.. image:: res/screenshots/TimerApp.png
   :alt: Countdown timer application running in the wasp-os simulator
   :width: 179

System apps:

.. image:: res/screenshots/DisaBLEApp.png
   :alt: Small application for disabling bluetooth to save power and enhance security
   :width: 179

.. image:: res/screenshots/LauncherApp.png
   :alt: Application launcher running on the wasp-os simulator
   :width: 179

.. image:: res/screenshots/SettingsApp.png
   :alt: Settings application running on the wasp-os simulator
   :width: 179

.. image:: res/screenshots/SoftwareApp.png
   :alt: Software selection app running on the wasp-os simulator
   :width: 179

.. image:: res/screenshots/FacesApp.png
   :alt: Switch watch faces
   :width: 179


Other apps: (The "blank" white screenshot is a flashlight app)

.. image:: res/screenshots/BeaconApp.png
   :alt: Flash the relatively powerful HRS LED repeatedly
   :width: 179

.. image:: res/screenshots/CalculatorApp.png
   :alt: Calculator running in the wasp-os simulator
   :width: 179

.. image:: res/screenshots/DemoApp.png
   :alt: Simple always-on demo for showing off wasp-os at conferences and shows
   :width: 179

.. image:: res/screenshots/FlashlightApp.png
   :alt: Torch application running on the wasp-os simulator
   :width: 179

.. image:: res/screenshots/GalleryApp.png
   :alt: Gallery application running on the wasp-os simulator
   :width: 179

.. image:: res/screenshots/HeartApp.png
   :alt: Heart rate application running on the wasp-os simulator
   :width: 179

.. image:: res/screenshots/HaikuApp.png
   :alt: Haiku application running in the wasp-os simulator
   :width: 179

.. image:: res/screenshots/LevelApp.png
   :alt: Shows a time as words in the wasp-os simulator
   :width: 179

.. image:: res/screenshots/MorseApp.png
   :alt: Morse translator/notepad application running on the wasp-os simulator
   :width: 179

.. image:: res/screenshots/PomodoroApp.png
   :alt: Customizable pomodoro app with randomized vibration patterns to make sure you notice
   :width: 179

.. image:: res/screenshots/PhoneFinderApp.png
   :alt: Find your phone by causing it to ring
   :width: 179

.. image:: res/screenshots/SportsApp.png
   :alt: Sports applications, a combined stopwatch and step counter
   :width: 179

.. image:: res/screenshots/StepCounterApp.png
   :alt: Step counter application running on the wasp-os simulator
   :width: 179

.. image:: res/screenshots/TestApp.png
   :alt: Self test application running a rendering benchmark on the simulator
   :width: 179

.. image:: res/screenshots/MusicPlayerApp.png
   :alt: Music Player running in the wasp-os simulator
   :width: 179

.. image:: res/screenshots/WeatherApp.png
   :alt: Weather application running in the wasp-os simulator
   :width: 179

