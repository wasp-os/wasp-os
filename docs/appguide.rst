Application Writer's Guide
==========================

.. contents::
    :local:

Introduction
------------

Wasp-os, the Watch Application System in Python, has one pervasive goal that
influences almost everything about it, from its name to its development
roadmap: make writing applications easy (and fun).

Applications that can be loaded, changed, adapted and remixed by the user
are what **really** distinguishes a smart watch from a "feature watch"[#]_.
In other words if we want a watch built around a tiny microcontroller to be
sufficiently "smart" then it has to be all about the applications.

This guide will help you get started writing applications for wasp-os. Have fun!

.. [#] The fixed function mobile phones that existed before iOS and Android
   took over the industry were retrospectively renamed "feature phones" to
   distinguish them from newer devices. Many of them were superficially similar
   to early Android devices but is was the application ecosystem that really
   made smart phones smart.

Hello World for wasp-os
~~~~~~~~~~~~~~~~~~~~~~~

Let's start by examining a simple "Hello, World!" application for wasp-os.

.. literalinclude:: hello.py
   :linenos:

There are a couple of points of interest:

1. Applications have a :py:attr:`~.TemplateApp.NAME`, which is shown in the
   launcher. Most applications also provide an :py:attr:`~.TemplateApp.ICON`
   but a default is displayed if this is omitted.
2. This example uses :py:meth:`~.TemplateApp.__init__` to initialize 
   the state of the application, this ensure the state remains "sticky" 
   when the application is activated and deactivated.
3. :py:meth:`~.TemplateApp.foreground` is the only mandatory application entry
   point and is responsible for redrawing the screen. This application does
   not implement :py:meth:`~.TemplateApp.background` because there is nothing
   for us to do!
4. The use of :py:meth:`~.TemplateApp._draw` is optional. We could just do
   the work in :py:meth:`~.TemplateApp.foreground` but this application follows
   a common wasp-os idiom that is normally used to pattern to distinguish a full
   refresh of the screen from an fast update (a redraw).

Application life-cycle
----------------------

Applications in wasp-os are triggered by and do all their processing
from calls their entry points. The entry points can be coarsely categorized
event notifications, timer callbacks (the application tick) and
system notifications.

System notifications control the application life-cycle and the entry point
calls, together with the implicit application states are shown below.

.. graphviz::

    digraph lifecycle {
        START -> BACKGROUND [ label=" __init__()   " ];
        BACKGROUND -> START [ label=" __del__()   " ];
        BACKGROUND -> ACTIVE [ label=" foreground()   " ];
        ACTIVE -> BACKGROUND [ label=" background()   " ];
        ACTIVE -> GO_TO_CLOCK [ label=" sleep() -> False   " ];
        GO_TO_CLOCK -> BACKGROUND [ label=" background()   " ];
        ACTIVE -> SLEEPING [ label=" sleep() -> True   " ];
        SLEEPING -> ACTIVE [ label=" wake()   " ];

        START [ shape=box ];
        BACKGROUND [ shape=box, style=rounded ]
        ACTIVE [ shape=box, style=rounded ]
        SLEEPING [ shape=box, style=rounded ]
        GO_TO_CLOCK [ label="GOTO ClockApp" ];
    }

When an application is initialized is enters the ``BACKGROUND`` state. A
backgrounded application will not execute but it should nevertheless 
maintain its user visible state whilst in the background. To conserve
memory wasp-os does not permit two applications to run simultaneously but
because each application preserves its state when in the background it will
appear to the user as though all applications are running all the time.

For example, a stopwatch application should record the time that it was started
and remember that start time, regardless of it's state, until either the
stopwatch is stopped of the application is destroyed.

A backgrounded application can enter the ``ACTIVE`` state via a call to
:py:meth:`~.TemplateApp.foreground`. When it is active the application owns the
screen and should draw and maintain its UI.

If the system manager want to put an active application to sleep then it will
call :py:meth:`~.TemplateApp.sleep`. If the application returns True then the
application will stop running (e.g. receive no events and no application tick)
but instead must wait to receive a notification via
:py:meth:`~.TemplateApp.wake` telling the application that the device 
is waking up and that it may update the screen if needed.

If an application does not support sleeping then it can simply not implement
:py:meth:`~.TemplateApp.sleep` (or :py:meth:`~.TemplateApp.wake`) although it
can also return False from :py:meth:`~.TemplateApp.sleep` if this is preferred.
In this case the system manager will automatically return to the default
application, typically the main clock face.

.. note::

    Most applications do not need to support :py:meth:`~.TemplateApp.sleep`
    since it is often a better user experience for the watch to return to the
    default application when they complete an interaction.
    
API primer
----------

This API primer introduces some of the most important and frequently used
interfaces for wasp-os. For more comprehensive coverage see the
:ref:`Wasp-os Reference Manual` which contains extensive API documentation
covering the entire of wasp-os, including its drivers.

System management
~~~~~~~~~~~~~~~~~

The system management API does provide a number of low-level calls that
can register new applications and navigate between them. However most
applications need not use these. Instead most applications use a small
set of methods. In particular almost all applictions need to call a couple of
methods from :py:meth:`~.TemplateApp.foreground` in order to register 
for notifications:

* :py:meth:`~.Manager.request_event` - register for UI events such as button
  presses and touch screen activity.
* :py:meth:`~.Manager.request_tick` - register to receive an application tick
  and specify the tick frequency.

Additionally if your application is a game or a similar program that should
not allow the watch to go to sleep then it should arrange to call
:py:meth:`~.Manager.keep_awake` from the application's
:py:meth:`~.TemplateApp.tick` method.

Drawing
~~~~~~~

Most applications using the drawing toolbox, :py:data:`wasp.watch.drawable`,
in order to handle the display. Applications are permitted to directly access
:py:data:`wasp.watch.display` if they require direct pixel access or want to
exploit specific features of the display hardware (inverse video, partial
display, etc) but for simple applications then the following simple drawing
functions are sufficient.

* :py:meth:`~.Draw565.blit` - blit an image to the display at specified (x, y)
  coordinates, image type is detected automatically
* :py:meth:`~.Draw565.fill` - fill a rectangle, without arguments the default
  is a black rectangle covering the entire screen which is useful to clear
  the screen prior to an update
* :py:meth:`~.Draw565.string` - render a string, optionally centring it
  automatically
* :py:meth:`~.Draw565.wrap` - automatically determine where to break a string
  so it can be rendered to a specified width

Most applications run some variant of the following code from their
:py:meth:`~.TemplateApp.foreground` or :py:meth:`~.TemplateApp._draw` methods
in order to clear the display ready for a redraw.

.. code-block:: python

   draw = wasp.watch.drawable
   draw.fill()
   # now use draw to render the rest of the screen

Some applications customize the above code slightly if they require a custom
background colour and it may even be omitted entirely if the application
explicitly draws every pixel on the display.

Finally, wasp-os provides a small number of widgets that allow common fragments
of logic and redrawing code to be shared between applications:

* :py:class:`.BatteryMeter`
* :py:class:`.ScrollingIndicator`

MicroPython
~~~~~~~~~~~

Many of the features of wasp-os are inherited directly from MicroPython_. It is
useful to have a basic understanding of MicroPython and, in particular, put
in a little time learning the best ways to copy with running
`MicroPython on microcontrollers`__.

.. _MicroPython: https://micropython.org/
__ http://docs.micropython.org/en/latest/reference/constrained.html


How to run your application
---------------------------

.. _Testing on the simulator:

Testing on the simulator
~~~~~~~~~~~~~~~~~~~~~~~~

wasp-os provides a simulator that can be used to test applications before
downloading them to the device. The simulator is useful for ensuring the
code is syntactically correct and that there are not major runtime problems
(e.g. missing symbols).

.. note::

    The simulator does not model the RAM or code size limits of the real
    device. It may still be necessary to tune the application for minimal
    footprint after testing on the simulator.

Firstly launch the simulator:

.. code-block:: sh

    sh$ make sim
    PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=.:wasp/boards/simulator:wasp \\
    python3 -i wasp/main.py
    MOTOR: set on
    BACKLIGHT: 2
    Watch is running, use Ctrl-C to stop

From the simulator console we can register the application with the following
code:

.. code-block:: python
   :linenos:

    ^C
    Traceback (most recent call last):
    ...
    KeyboardInterrupt
    >>> from myapp import MyApp
    >>> wasp.system.register(MyApp())
    >>> wasp.system.run()
    Watch is running, use Ctrl-C to stop

When an application is registered it does not start automatically but it will
have been added to the launcher and you will be able to select in the simulator
by using the Arrow keys to bring up the launcher and then clicking on your
application.

The application can also be registered automatically when you load the
simulator if you add it to ``wasp/main.py``. Try adding lines 5 and 6 from
the above example into this file (between ``import wasp`` and
``wasp.system.run()``).

Testing on the device
~~~~~~~~~~~~~~~~~~~~~

If we have an application under development when we can launch a quick test
that does not result in the application being permanently stored on the device.
Providing there is enough available RAM then this can lead to a very quick
edit-test cycles.

Try:

.. code-block:: sh

    sh$ tools/wasptool \\
            --exec myapp.py \\
            --eval "wasp.system.register(MyApp())"
    Preparing to run myapp.py:
    [##################################################] 100% 

Like the simulator, when an application is registered it does not start 
automatically but it will have been added to the launcher and can be launched
using the normal gestures to control the device.

.. note::

    If the progress bar jams at the same point each time then it is likely your
    application is too large to be compiled on the target. You may have to
    adopt the frozen module approach from the next section.

Making it permanent
~~~~~~~~~~~~~~~~~~~

To ensure you application survives a system reset (press the hardware 
button for around five seconds until the splash screen is seen, wait 
five seconds and then press again) then we must copy it to the device
and ensure it gets launched during system startup.

.. note::

    Applications stored in external FLASH have a greater RAM overhead than
    applications that are frozen into the wasp-os binary. See next section for
    additional details.

To copy your application to the external FLASH try:

.. code-block:: sh

    sh$ ./tools/wasptool --upload myapp.py
    Uploading myapp.py:
    [##################################################] 100% 

At this point your application is stored on the external FLASH but it will
not automatically be loaded. This requires you to update the ``main.py`` file
stored in the external FLASH. When wasp-os runs for the first time it
automatically generates this file (using ``wasp/main.py`` as a template)
and copies it to the external FLASH. After this point ``main.py`` is user
modifiable and can be used to tweak the configuration of the watch before
it starts running.

Edit ``wasp/main.py`` to add the following two lines between ``import wasp``
and the ``wasp.system.run()``:

.. code-block:: python

    from myapp import MyApp
    wasp.system.register(MyApp())

Having done that we can use ``wasptool`` to upload the modified file
to the watch:

.. code-block:: sh

    sh$ ./tools/wasptool --upload wasp/main.py
    Uploading wasp/main.py:
    [##################################################] 100% 

.. note::

    If the new code on the watch throws an exception (including an
    out-of-memory exception) then your watch will display a black screen at
    startup. If that happens, and you don't know how to debug the problem, then
    you can use wasptool to restore the original version of main.py .

Freezing your application into the wasp-os binary
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Freezing your application causes it to consume dramatically less RAM.  That is
because the code is both pre-compiled (meaning we don't need any RAM budget to
run the compiler) **and** it can execute directly from the internal FLASH
memory.

Freezing your application simply requires you to modify the ``manifest.py``
file for your board (e.g. ``wasp/boards/pinetime/manifest.py``) to include
your application and then the whole binary must be re-compiled as normal.

After that you an use the same technique described in the previous 
section to add an import and register for you application to ``main.py``

.. note::

    The micropython import path "prefers" frozen modules to those found in the
    external filesystem. If your application is both frozen and copied to
    external FLASH then the frozen version will be loaded.

    In many cases it is possible to avoid rebuilding the binary in order to
    test new features by parsing the code in the global namespace and then
    patching it into the existing code. For example the following can be used
    to adopt a new version of the CST816S driver:

    .. code-block::

        ./tools/wasptool\
            --exec wasp/drivers/cst816s.py\
            --eval "watch.touch = CST816S(watch.i2c)"`
 
Application entry points
------------------------

Applications provide entry points for the system manager to use to notify
the application of a change in system state or an user interface event.

.. automodule:: apps.template
   :members:
   :private-members:
   :special-members:
