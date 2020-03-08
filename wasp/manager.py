import gc
import machine

from apps.clock import ClockApp
from apps.flashlight import FlashlightApp
from apps.testapp import TouchTestApp

DOWN = 1
UP = 2
LEFT = 3
RIGHT = 4

EVENT_TOUCH = 0x0001
EVENT_BUTTON = 0x0002

class Manager(object):
    def __init__(self, watch):
        self.watch = watch

        self.app = None

        self.applications = [
                ClockApp(),
                FlashlightApp(),
                TouchTestApp()
            ]

        self.watch.display.poweron()
        self.switch(self.applications[0])
        self.watch.backlight.set(2)

        self.sleep_at = watch.rtc.uptime + 90
        self.charging = True

    def switch(self, app):
        if self.app:
            self.app.background()

        # Clear out any configuration from the old application
        self.event_mask = 0
        self.tick_period_ms = 0
        self.tick_expiry = None

        self.app = app
        self.watch.display.mute(True)
        app.foreground(self)
        self.watch.display.mute(False)

    def navigate(self, direction=None):
        """Navigate between different applications.

        Currently the direction is ignored.
        """
        app_list = self.applications

        if direction == DOWN:
            i = app_list.index(self.app) + 1
            if i >= len(app_list):
                i = 0
            self.switch(app_list[i])
        elif direction == UP:
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
        self.tick_expiry = self.watch.rtc.get_uptime_ms() + period_ms

    def handle_event(self, event):
        self.sleep_at = self.watch.rtc.uptime + 15

        if event[0] < 5:
            self.navigate(event[0])
        elif event[0] == 5 and self.event_mask & EVENT_TOUCH:
            self.app.touch(event)

    def tick(self):
        rtc = self.watch.rtc

        if self.sleep_at:
            if rtc.update() and self.tick_expiry:
                now = rtc.get_uptime_ms()

                if self.tick_expiry <= now:
                    ticks = 0
                    while self.tick_expiry <= now:
                        self.tick_expiry += self.tick_period_ms
                        ticks += 1
                    self.app.tick(ticks)

            if self.watch.button.value():
                self.sleep_at = self.watch.rtc.uptime + 15

            event = self.watch.touch.get_event()
            if event:
                self.handle_event(event)

            if self.watch.rtc.uptime > self.sleep_at:
                self.watch.backlight.set(0)
                if not self.app.sleep():
                    self.switch(self.applications[0])
                    self.app.sleep()
                self.watch.display.poweroff()
                self.charging = self.watch.battery.charging()
                self.sleep_at = None

            gc.collect()
        else:
            self.watch.rtc.update()

            charging = self.watch.battery.charging()
            if self.watch.button.value() or self.charging != charging:
                self.watch.display.poweron()
                self.app.wake()
                self.watch.backlight.set(2)

                # Discard any pending touch events
                _ = self.watch.touch.get_event()

                self.sleep_at = self.watch.rtc.uptime + 15

    def run(self):
        """Run the system manager synchronously.

        This allows all watch management activities to handle in the
        normal execution context meaning any exceptions and other problems
        can be observed interactively via the console.
        """
        while True:
            self.tick()
            machine.deepsleep()
