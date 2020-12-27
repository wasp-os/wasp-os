.. _Application Library:

Application Library
===================

.. contents::
    :local:

Built-in
--------

The built-in application are summarised below but because these apps are
treated as examples they are described in detail as part of the
:ref:`Wasp-os Reference Manual`: 

 * :py:class:`.ClockApp`
 * :py:class:`.FlashlightApp`
 * :py:class:`.LauncherApp`
 * :py:class:`.PagerApp`
 * :py:class:`.TestApp`
 * :py:class:`.TemplateApp``

Watch faces
-----------

.. automodule:: apps.chrono

This application is very simple and largely serves as an example of how to
implement traditional watch faces.
It is not included by default in any image.
Instead it can be transferred to the device dynamically using wasptool:

.. code-block:: sh

    ./tools/wasptool --exec wasp/apps/chrono.py --eval 'wasp.system.register(ChronoApp())'

.. automodule:: apps.fibonacci_clock

This app is enabled by default in the simulator.
The app is also frozen into the firmware image but it is disabled by
default in order to keep RAM available for user developed applications.
It can be enabled by modifying ``main.py``.

Games
-----

.. automodule:: apps.gameoflife

This app is enabled by default in the simulator.
The app is also frozen into the firmware image but it is disabled by
default in order to keep RAM available for user developed applications.
It can be enabled by modifying ``main.py``.

.. automodule:: apps.snake

This app is enabled by default in the simulator.
The app is also frozen into the firmware image but it is disabled by
default in order to keep RAM available for user developed applications.
It can be enabled by modifying ``main.py``.

Integration
-----------

.. automodule:: apps.alarm

This app is enabled by default in the simulator.
The app is also frozen into the firmware image but it is disabled by
default in order to keep RAM available for user developed applications.
It can be enabled by modifying ``main.py``.

.. automodule:: apps.musicplayer

This app is enabled by default in the simulator.
The app is also frozen into the firmware image but it is disabled by
default in order to keep RAM available for user developed applications.
It can be enabled by modifying ``main.py``.
