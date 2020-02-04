import clock
import gc
import machine

class Manager(object):
    def __init__(self, watch):
        self.watch = watch
        self.switch(clock.ClockApp())
        self.sleep_at = watch.rtc.uptime + 90
        self.charging = True

    def switch(self, app):
        self.app = app
        app.draw(self.watch)

    def tick(self):
        if self.sleep_at:
            if self.watch.rtc.update():
                self.app.update(self.watch)

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
                self.app.update(self.watch)
                self.watch.backlight.set(2)

                self.sleep_at = self.watch.rtc.uptime + 15


    def run(self):
        while True:
            self.tick()
            machine.deepsleep()
