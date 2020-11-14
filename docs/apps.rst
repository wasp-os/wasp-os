.. _Application Library:

Application Library
===================

.. contents::
    :local:

Built-in
--------

The built-in application are summarised below but since these apps are
considers to be examples they are described in detail as part of the
:ref:`Wasp-os Reference Manual`: 

 * :py:class:`.ClockApp`
 * :py:class:`.FlashlightApp`
 * :py:class:`.LauncherApp`
 * :py:class:`.PagerApp`
 * :py:class:`.TestApp`
 * :py:class:`.TemplateApp``

Watch faces
-----------

.. automodule:: apps.fibonacci_clock

This is enabled by default in the simulator. The app is bundled in the
firmware image but it is disabled by default to keep RAM available for
user developed applications. It can be enabled by modifying ``main.py``.

Games
-----

.. automodule:: apps.gameoflife

This is enabled by default in the simulator. The app is bundled in the
firmware image but it is disabled by default to keep RAM available for
user developed applications. It can be enabled by modifying ``main.py``.
