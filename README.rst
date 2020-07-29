Watch Application System in Python
==================================

Introduction
------------

Although still in its infancy wasp-os provides many example applications
including a simple digital clock, a stopwatch, a step counter and a heart rate
monitor. All of these, together with access to the MicroPython REPL for
interactive tweaking and testing, are running on `PineTime
<https://www.pine64.org/pinetime/>`_.  It keeps time well and has enough power
saving functions implemented that it can survive for well over 72 hours between
charges so even at this early stage it is functional as a wearable timepiece.

Wasp-os includes a robust bootloader based on the Adafruit NRF52
Bootloader. It has been extended to make it robust for development on
form-factor devices without a reset button, power switch, SWD debugger
or UART. This allows us to confidently develop on sealed devices relying
only on BLE for updates.

Videos
------

.. image:: https://img.youtube.com/vi/lIo2-djNR48/0.jpg
   :target: https://www.youtube.com/watch?v=lIo2-djNR48
   :alt: wasp-os: Open source heart rate monitoring for Pine64 PineTime
   :width: 320
   :height: 240

`Open source heart rate monitoring for Pine64 PineTime <https://www.youtube.com/watch?v=lIo2-djNR48>`_

.. image:: https://img.youtube.com/vi/YktiGUSRJB4/0.jpg
   :target: https://www.youtube.com/watch?v=YktiGUSRJB4
   :alt: An M2 pre-release running on Pine64 PineTime
   :width: 320
   :height: 240

`An M2 pre-release running on Pine64 PineTime <https://www.youtube.com/watch?v=YktiGUSRJB4>`_

.. image:: https://img.youtube.com/vi/tuk9Nmr3Jo8/0.jpg
   :target: https://www.youtube.com/watch?v=tuk9Nmr3Jo8
   :alt: How to develop wasp-os python applications on a Pine64 PineTime
   :width: 320
   :height: 240

`How to develop wasp-os python applications on a Pine64 PineTime <https://www.youtube.com/watch?v=tuk9Nmr3Jo8>`_

.. image:: https://img.youtube.com/vi/kf1VHj587Mc/0.jpg
   :target: https://www.youtube.com/watch?v=kf1VHj587Mc
   :alt: Developing for Pine64 PineTime using wasp-os and MicroPython
   :width: 320
   :height: 240

`Developing for Pine64 PineTime using wasp-os and MicroPython <https://www.youtube.com/watch?v=kf1VHj587Mc>`_

Documentation
-------------

Wasp-os is has `extensive documentation <https://wasp-os.readthedocs.io>`_
which includes a detailed `Applicaiton Writer's Guide
<https://wasp-os.readthedocs.io/en/latest/appguide.html>`_ to help you
get started coding for wasp-os as quickly as possible.

Building from source
--------------------

Building wasp-os and launching the wasp-os simulator requires Python 3.6
(or later) and the following python modules: click, numpy, pexpect, PIL
(or Pillow), pyserial, pysdl2.

On Debian Buster the required python modules can be obtained using the
following commands:

.. code-block:: sh

    sudo apt install \
      git build-essential libsdl2-2.0.0 \
      python3-click python3-numpy python3-pexpect \
      python3-pil python3-pip python3-serial
    pip3 install --user pysdl2

You will also need a toolchain for the Arm Cortex-M4. wasp-os is developed and
tested using the `GNU-RM toolchain
<https://developer.arm.com/tools-and-software/open-source-software/developer-tools/gnu-toolchain/gnu-rm>`_
(9-2019-q4) from Arm.

.. note::

    There are known problems with toolchains older than gcc-7.3 when
    link time optimization is enabled during the MicroPython build
    (and LTO is enabled by default).

Get the code from
`https://github.com/daniel-thompson/wasp-os <https://github.com/daniel-thompson/wasp-os>`_ :

.. code-block:: sh

   git clone https://github.com/daniel-thompson/wasp-os
   cd wasp-os
   make submodules
   make softdevice

Build the firmware:

.. code-block:: sh

   make -j `nproc` BOARD=pinetime all

Finally to test out ideas and concepts on the simulator try:

.. code-block:: sh

    make sim

See :ref:`Testing on the simulator` for more details on how
to use the simulator.

Getting Started
---------------

Wasp-os can be installed without using any tools onto the following
devices:

 * Pine64 PineTime (developer edition)
 * Colmi P8

The
`Installation Guide <https://wasp-os.readthedocs.io/en/latest/install.html>`_
contains detailed instructions on how to install wasp-os.

At the end of the install process your watch will show the time (03:00)
together with a date and battery meter. When the watch goes into power
saving mode you can use the button to wake it again.

At this point you will also be able to use the Nordic UART Service to
access the MicroPython REPL. You can use ``tools/wasptool --console``
to access the MicroPython REPL.

To set the time and restart the main application:

.. code-block:: python

   ^C
   watch.rtc.set_localtime((yyyy, mm, dd, HH, MM, SS))
   wasp.system.run()

Or just use:

.. code-block:: sh

   ./tools/wasptool --rtc

which can run these commands automatically.

As mentioned above there are many drivers and features still to be
developed, see the :ref:`Roadmap` for current status.

Screenshots
-----------

.. image:: res/clock_app.jpg
   :alt: wasp-os digital clock app running on PineTime
