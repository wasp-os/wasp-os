# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 Daniel Thompson
"""WASP system management (including constants)

.. data:: system = Manager()

   system is the system-wide instance of the Manager class. Applications
   can use this instance to access system services.
"""

import gc
import machine
import watch
import widgets

from apps.clock import ClockApp
from apps.flashlight import FlashlightApp
from apps.testapp import TestApp

class Direction():
    """Enumerated directions.

    MicroPython does not implement the enum module so Direction
    is simply a regular object which acts as a namespace.
    """
    DOWN = 1
    UP = 2
    LEFT = 3
    RIGHT = 4

class Event():
    """Enumerated event types
    """
    TOUCH = 0x0001
    SWIPE_LEFTRIGHT = 0x0002
    SWIPE_UPDOWN = 0x0004
    BUTTON = 0x0008

class Manager():
    """WASP system manager

    The manager is responsible for handling top-level UI events and
    dispatching them to the foreground application. It also provides
    services to the application.

    The manager is expected to have a single system-wide instance
    which can be accessed via :py:data:`wasp.system` .
    """

    def __init__(self):
        self.app = None

        self.applications = [
                ClockApp(),
                FlashlightApp(),
                TestApp()
            ]
        self.charging = True

        self._brightness = 2

    @property
    def brightness(self):
        """Cached copy of the brightness current written to the hardware."""
        return self._brightness

    @brightness.setter
    def brightness(self, value):
        self._brightness = value
        watch.backlight.set(self._brightness)

    def switch(self, app):
        """Switch to the requested application.
        """
        if self.app:
            self.app.background()
        else:
            # System start up...
            watch.display.poweron()
            watch.display.mute(True)
            watch.backlight.set(self._brightness)
            self.sleep_at = watch.rtc.uptime + 90

        # Clear out any configuration from the old application
        self.event_mask = 0
        self.tick_period_ms = 0
        self.tick_expiry = None

        self.app = app
        watch.display.mute(True)
        app.foreground()
        watch.display.mute(False)

    def navigate(self, direction=None):
        """Navigate to a new application.

        Left/right navigation is used to switch between applications in the
        quick application ring. Applications on the ring are not permitted
        to subscribe to :py:data`Event.SWIPE_LEFTRIGHT` events.

        :param int direction: The direction of the navigation
        """
        app_list = self.applications

        if direction == Direction.LEFT:
            i = app_list.index(self.app) + 1
            if i >= len(app_list):
                i = 0
            self.switch(app_list[i])
        elif direction == Direction.RIGHT:
            i = app_list.index(self.app) - 1
            if i < 0:
                i = len(app_list)-1
            self.switch(app_list[i])

    def request_event(self, event_mask):
        """Subscribe to events.

        :param int event_mask: The set of events to subscribe to.
        """
        self.event_mask |= event_mask

    def request_tick(self, period_ms=None):
        """Request (and subscribe to) a periodic tick event.

        Note: With the current simplistic timer implementation sub-second
        tick intervals are not possible.
        """
        self.tick_period_ms = period_ms
        self.tick_expiry = watch.rtc.get_uptime_ms() + period_ms

    def keep_awake(self):
        """Reset the keep awake timer."""
        self.sleep_at = watch.rtc.uptime + 15

    def sleep(self):
        """Enter the deepest sleep state possible.
        """
        watch.backlight.set(0)
        if not self.app.sleep():
            self.switch(self.applications[0])
            self.app.sleep()
        watch.display.poweroff()
        self.charging = watch.battery.charging()
        self.sleep_at = None

    def wake(self):
        """Return to a running state.
        """
        watch.display.poweron()
        self.app.wake()
        watch.backlight.set(self._brightness)

        # Discard any pending touch events
        _ = watch.touch.get_event()

        self.keep_awake()

    def _handle_event(self, event):
        """Process an event.
        """
        self.keep_awake()

        event_mask = self.event_mask
        if event[0] < 5:
            updown = event[0] == 1 or event[0] == 2
            if (bool(event_mask & Event.SWIPE_UPDOWN) and updown) or \
               (bool(event_mask & Event.SWIPE_LEFTRIGHT) and not updown):
                if not self.app.swipe(event):
                    self.navigate(event[0])
            else:
                self.navigate(event[0])
        elif event[0] == 5 and self.event_mask & Event.TOUCH:
            self.app.touch(event)

    def _tick(self):
        """Handle the system tick.

        This function may be called frequently and includes short
        circuit logic to quickly exit if we haven't reached a tick
        expiry point.
        """
        rtc = watch.rtc

        if self.sleep_at:
            if rtc.update() and self.tick_expiry:
                now = rtc.get_uptime_ms()

                if self.tick_expiry <= now:
                    ticks = 0
                    while self.tick_expiry <= now:
                        self.tick_expiry += self.tick_period_ms
                        ticks += 1
                    self.app.tick(ticks)

            if watch.button.value():
                self.keep_awake()

            event = watch.touch.get_event()
            if event:
                self._handle_event(event)

            if watch.rtc.uptime > self.sleep_at:
                self.sleep()

            gc.collect()
        else:
            watch.rtc.update()

            charging = watch.battery.charging()
            if watch.button.value() or self.charging != charging:
                self.wake()

    def run(self):
        """Run the system manager synchronously.

        This allows all watch management activities to handle in the
        normal execution context meaning any exceptions and other problems
        can be observed interactively via the console.
        """
        if not self.app:
            self.switch(self.applications[0])

        # Reminder: wasptool uses this string to confirm the device has
        # been set running again.
        print('Watch is running, use Ctrl-C to stop')

        while True:
            self._tick()
            # Currently there is no code to control how fast the system
            # ticks. In other words this code will break if we improve the
            # power management... we are currently relying on no being able
            # to stay in the low-power state for very long.
            machine.deepsleep()

system = Manager()
