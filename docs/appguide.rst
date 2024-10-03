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
"smart" then it has to be all about the applications.

This guide will help you get started writing applications for wasp-os. Have fun!

.. [#] The fixed function mobile phones that existed before iOS and Android
   took over the industry were retrospectively renamed "feature phones" to
   distinguish them from newer devices. Many of them were superficially similar
   to early Android devices but is was the application ecosystem that really
   made smart phones into what they are today.

Hello World for wasp-os
~~~~~~~~~~~~~~~~~~~~~~~

Let's start by examining a simple "Hello, World!" application for wasp-os.

.. literalinclude:: hello.py
   :linenos:

Some of the key points of interest in this example application are:

1. Applications have a :py:attr:`~.TemplateApp.NAME`, which is shown in the
   launcher. Most applications also provide an :py:attr:`~.TemplateApp.ICON`
   but a default will be displayed if this is omitted.
2. This example uses :py:meth:`~.TemplateApp.__init__` to initialize
   the state of the application, these variables are used to remember
   the state of the application when when it is deactivated.
3. :py:meth:`~.TemplateApp.foreground` is the only mandatory application entry
   point and it is responsible for redrawing the screen. This application does
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
system actions.

System actions control the application life-cycle and that lifecyle is
shown below. The system actions are used to tell the application about
any change in its lifecycle.

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
maintain its user visible state whilst deactivated. To conserve
memory wasp-os does not permit two applications to run simultaneously but
because each application remembers its state when it is not running then it
will appear to the user as though all applications are running all the time.

For example, a stopwatch application should record the time that it was started
and remember that start time, regardless of whether it is running or not so
that when it restarted is can continue to run as the user expects.

A backgrounded application enters the ``ACTIVE`` state via a call to
:py:meth:`~.TemplateApp.foreground`. When it is active the application owns the
screen and must draw and maintain its user interface.

If the system manager wants to put the watch to sleep then it will tell the
active application to :py:meth:`~.TemplateApp.sleep`.
If the application returns True then the application will remain active
whilst the watch is asleep.
It will receive no events nor the application tick whilst the system is
asleep and, instead, must wait for a :py:meth:`~.TemplateApp.wake` notification
telling the application that the device is waking up and that it may
update the screen if needed.

If an application does not support sleeping then it can simply not implement
:py:meth:`~.TemplateApp.sleep` or :py:meth:`~.TemplateApp.wake`.
In this case the system manager will automatically return to the default
application, typically the main clock face.

Some applications may support sleeping only under certain circumstances. For
example a stopwatch may choose to remain active when the watch sleeps only if
the stopwatch is running.
This type of application must implement :py:meth:`~.TemplateApp.sleep` and
return False when it does not want to remain active when the system
resumes.

.. note::

    Most applications should not implement :py:meth:`~.TemplateApp.sleep`
    since it is often a better user experience for the watch to return to the
    default application when they complete an interaction.

API primer
----------

This API primer introduces some of the most important and frequently used
interfaces in wasp-os. For more comprehensive coverage see the
:ref:`Wasp-os Reference Manual` which contains extensive API documentation
covering the entire of wasp-os, including its drivers.

System management
~~~~~~~~~~~~~~~~~

The system management API provides a number of low-level calls that
can register new applications and navigate between them. However most
applications do not need to make these low level calls and will use
a much smaller set of methods.

Applictions must call a couple of functions from their
:py:meth:`~.TemplateApp.foreground` in order to register for
event notifications and timer callbacks:

* :py:meth:`~.Manager.request_event` - register for UI events such as button
  presses and touch screen activity.
* :py:meth:`~.Manager.request_tick` - register to receive an application tick
  and specify the tick frequency.

Additionally if your application is a game or a similar program that should
not allow the watch to go to sleep when it is running then it should
arrange to call :py:meth:`~.Manager.keep_awake` from the application's
:py:meth:`~.TemplateApp.tick` method.

Drawing
~~~~~~~

Most applications using the drawing toolbox, :py:data:`wasp.watch.drawable`,
in order to handle the display. Applications are permitted to directly access
:py:data:`wasp.watch.display` if they require direct pixel access or want to
exploit specific features of the display hardware (inverse video, partial
display, etc) but for most applications the drawing toolbox provides
convenient and optimized drawing functions.

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
a little time into learning the best practices when running
`MicroPython on microcontrollers`__.

.. _MicroPython: https://micropython.org/
__ http://docs.micropython.org/en/latest/reference/constrained.html

App naming conventions and placement
------------------------------------

Your app must be named in a specific way and placed in the /apps directory to be compatible with wasp-os.
Watch faces follow the same rules but are placed in the /watch_faces directory.

1. The name of the python file must be in snake case (ie: music_player.py)
2. The class of your app must be the name of the file in pascal case with "App" appended (ie: MusicPlayerApp)
3. The NAME variable in your app must short and will be used on the launcher screen (ie: NAME = 'Music')

If you wish to submit your app to the project it must additionally meet these requirements:

1. The app must be added to docs/apps.rst
2. The app must be added to the README.rst
3. A simulator screenshot must exist in the /res/screenshots directory having the name of the app class (ie: MusicPlayerApp.png). Press s in the simulator to take a screenshot.
4. The app must include a README comment at the top of the file (see existing apps)
5. The app README must include a link to the simulator screenshot in the /res/screenshots directory
6. If your app has an icon (encouraged) than the image used to generate the RLE must be in the /res/icons directory. Its name should be the snake case name of the app file with "_icon" appended. (ie: music_player_icon.png)

To check if your app meets these requirements you can run the following command:

.. code-block:: sh

    make check


How to run your application
---------------------------

.. _Testing on the simulator:

Testing on the simulator
~~~~~~~~~~~~~~~~~~~~~~~~

wasp-os includes a simulator that can be used to test applications before
downloading them to the device. The simulator is useful for ensuring the
code is syntactically correct and that there are not major runtime problems
such as misspelt symbol names.

.. note::

    The simulator does not model the RAM or code size limits of the real
    device. It may still be necessary to tune the application for minimal
    footprint after testing on the simulator.

To launch the simulator:

.. code-block:: sh

    sh$ make sim
    PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=.:wasp/boards/simulator:wasp \\
    python3 -i wasp/boards/simulator/main.py
    MOTOR: set on
    BACKLIGHT: 2
    Watch is running, use Ctrl-C to stop

From the simulator console we can register the application with the following
commands:

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
by swiping or using the Arrow keys to bring up the launcher and then clicking
on your application.

The application can also be registered automatically when you load the
simulator if you add it to ``wasp/boards/simulator/main.py``. Try adding lines
5 and 6 from the above example into this file (between ``import wasp`` and
``wasp.system.run()``).

The simulator accepts gestures such as up/down and left/right swipes but the
simulator also accepts keystrokes for convenience. The arrow keys simulate
swipes and the Tab key simulates the physical button, whilst the 's' key
can be used to capture screen shots to add to the documentation for your
application.

Testing on the device
~~~~~~~~~~~~~~~~~~~~~

When an application is under development it is best to temporarily load
your application without permanently stored on the device.
Providing there is enough available RAM then this can lead to a very quick
edit-test cycles.

Try:

.. code-block:: sh

    sh$ tools/wasptool \\
            --exec myapp.py \\
            --eval "wasp.system.register(MyApp())"
    Preparing to run myapp.py:
    [##################################################] 100%

Like the simulator, when an application is registered it is added to the
launcher and it does not start automatically.

.. note::

    If the progress bar jams at the same point each time then it is likely your
    application is too large to be compiled on the target. You may have to
    adopt the frozen module approach from the next section.

To remove the application simply reboot the watch by pressing and
holding the physical button until the watch enters OTA mode (this
takes around five seconds). Once the watch is in OTA mode then
press the physical button again to return to normal mode with the
application cleared out.

.. _Uploading in source code form:

Uploading in source code form
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To ensure you application survives a reboot then we must copy it to the
device and ensure it gets launched during system startup.

.. note::

    Applications stored in external FLASH have a greater RAM overhead than
    applications that are frozen into the wasp-os binary. If you app does
    not fix then see next section for additional details on how to embed
    your app in the wasp-os binary itself..

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

Edit ``wasp/main.py`` to add the following two lines and the end of the file
(after the ``wasp.system.schedule()``:

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

Uploading in binary form
~~~~~~~~~~~~~~~~~~~~~~~~

Some applications are too large to be compiled on the target. These applications
need to be pre-compiled and can then either be uploaded in binary form to the
wasp-os filesystem or
:ref:`included in the firmware image<Freezing your application into the wasp-os binary>`
to further reduce the RAM overhead.

To pre-compile your application:

.. code-block:: sh

    sh$ ./micropython/mpy-cross/mpy-cross -mno-unicode -march=armv7m myapp.py

To copy the binary to the wasp-os filesystem try:

.. code-block:: sh

    sh$ ./tools/wasptool --binary --upload myapp.mpy
    Uploading myapp.mpy:
    [##################################################] 100%

At this point your application is stored on the external FLASH but it will
not automatically be loaded but it can be imported using ``import myapp``.
The application can be registered from ``main.py`` using exactly the same
technique as :ref:`uploads in source code<Uploading in source code form>`.

.. _Freezing your application into the wasp-os binary:

Freezing your application into the wasp-os binary
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Freezing your application causes it to consume dramatically less RAM.  That is
because they can execute directly from the internal FLASH rather than running
from RAM. Additionally the code is pre-compiled, which also means we don't
need any RAM budget to run the compiler.

To freeze your app into the wasp-os binary add it to the wasp.toml file.

.. note::

    The micropython import path "prefers" frozen modules to those found in the
    external filesystem. If your application is both frozen and copied to
    external FLASH then the frozen version will be loaded.

    In many cases it is possible to avoid rebuilding the binary in order to
    test new features by directly parsing the code in the global
    namespace (e.g. using ``wasptool --exec`` rather than ``wasptool --upload``
    combined with ``import``). With the code in the global namespace it can
    then be patched into the system. For example the following can be used
    to adopt a new version of the CST816S driver:

    .. code-block:: sh

        ./tools/wasptool\
            --exec wasp/drivers/cst816s.py\
            --eval "watch.touch = CST816S(watch.i2c)"`

Auto loading applications in flash
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If there is not enough room on your device to freeze your application
into the wasp-os binary you can still have it automatically added to
the software list by uploading it to the apps directory of your device.
The application will still have the RAM constraints of an app in flash.

To automatically have your uploaded application added to the software:

.. code-block:: sh

    sh$ ./tools/wasptool --binary --upload myapp.mpy --as apps/myapp.mpy
    Uploading apps/myapp.mpy:
    [##################################################] 100%

To delete a file from the device:

.. code-block:: sh

    sh$ ./tools/wasptool --console
    >>>import os
    >>>os.remove("apps/myapp.mpy")
    >>>del os

Application entry points
------------------------

Applications provide entry points for the system manager to use to notify
the application of a change in system state or an user interface event.

.. automodule:: template
   :members:
   :private-members:
   :special-members:
