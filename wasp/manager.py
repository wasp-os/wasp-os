import clock
import gc
import machine

EVENT_TICK = 0x100
EVENT_KEYMASK = 0xff

class Manager(object):
    def __init__(self, watch):
        self.watch = watch

        self.app = None
        self.switch(clock.ClockApp())
        self.sleep_at = watch.rtc.uptime + 90
        self.charging = True

    def switch(self, app):
        if self.app:
            self.app.background(self)

        # Clear out any configuration from the old application
        self.tick_period_ms = 0
        self.tick_expiry = None

        self.app = app
        app.foreground(self)

    def request_tick(self, period_ms=None):
        """Request (and subscribe to) a periodic tick event.

        Note: With the current simplistic timer implementation sub-second
        tick intervals are not possible.
        """
        self.tick_period_ms = period_ms
        self.tick_expiry = self.watch.rtc.get_uptime_ms() + period_ms

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

            if self.watch.rtc.uptime > self.sleep_at:
                self.watch.backlight.set(0)
                self.watch.display.poweroff()
                self.charging = self.watch.battery.charging()
                self.sleep_at = None

            gc.collect()
        else:
            self.watch.rtc.update()

            charging = self.watch.battery.charging()
            if self.watch.button.value() or self.charging != charging:
                self.watch.display.poweron()
                self.app.tick(None)
                self.watch.backlight.set(2)

                self.sleep_at = self.watch.rtc.uptime + 15


    def run(self):
        while True:
            self.tick()
            machine.deepsleep()
