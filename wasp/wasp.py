# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 Daniel Thompson

import gc
import machine
import watch
import widgets

from apps.clock import ClockApp
from apps.flashlight import FlashlightApp
from apps.testapp import TestApp

DOWN = 1
UP = 2
LEFT = 3
RIGHT = 4

EVENT_TOUCH = 0x0001
EVENT_SWIPE_LEFTRIGHT = 0x0002
EVENT_SWIPE_UPDOWN = 0x0004
EVENT_BUTTON = 0x0008

class Manager(object):
    def __init__(self):
        self.app = None

        self.applications = [
                ClockApp(),
                FlashlightApp(),
                TestApp()
            ]
        self.charging = True

    def switch(self, app):
        if self.app:
            self.app.background()
        else:
            # System start up...
            watch.display.poweron()
            watch.display.mute(True)
            watch.backlight.set(2)
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
        """Navigate between different applications.

        Currently the direction is ignored.
        """
        app_list = self.applications

        if direction == LEFT:
            i = app_list.index(self.app) + 1
            if i >= len(app_list):
                i = 0
            self.switch(app_list[i])
        elif direction == RIGHT:
            i = app_list.index(self.app) - 1
            if i < 0:
                i = len(app_list)-1
            self.switch(app_list[i])

    def request_event(self, event_mask):
        self.event_mask |= event_mask

    def request_tick(self, period_ms=None):
        """Request (and subscribe to) a periodic tick event.

        Note: With the current simplistic timer implementation sub-second
        tick intervals are not possible.
        """
        self.tick_period_ms = period_ms
        self.tick_expiry = watch.rtc.get_uptime_ms() + period_ms

    def handle_event(self, event):
        self.sleep_at = watch.rtc.uptime + 15

        event_mask = self.event_mask
        if event[0] < 5:
            updown = event[0] == 1 or event[0] == 2
            if (bool(event_mask & EVENT_SWIPE_UPDOWN) and updown) or \
               (bool(event_mask & EVENT_SWIPE_LEFTRIGHT) and not updown):
                if not self.app.swipe(event):
                    self.navigate(event[0])
            else:
                self.navigate(event[0])
        elif event[0] == 5 and self.event_mask & EVENT_TOUCH:
            self.app.touch(event)

    def tick(self):
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
                self.sleep_at = watch.rtc.uptime + 15

            event = watch.touch.get_event()
            if event:
                self.handle_event(event)

            if watch.rtc.uptime > self.sleep_at:
                watch.backlight.set(0)
                if not self.app.sleep():
                    self.switch(self.applications[0])
                    self.app.sleep()
                watch.display.poweroff()
                self.charging = watch.battery.charging()
                self.sleep_at = None

            gc.collect()
        else:
            watch.rtc.update()

            charging = watch.battery.charging()
            if watch.button.value() or self.charging != charging:
                watch.display.poweron()
                self.app.wake()
                watch.backlight.set(2)

                # Discard any pending touch events
                _ = watch.touch.get_event()

                self.sleep_at = watch.rtc.uptime + 15

    def run(self):
        """Run the system manager synchronously.

        This allows all watch management activities to handle in the
        normal execution context meaning any exceptions and other problems
        can be observed interactively via the console.
        """
        if not self.app:
            self.switch(self.applications[0])

        print('Watch is running, use Ctrl-C to stop')

        while True:
            self.tick()
            machine.deepsleep()

system = Manager()
