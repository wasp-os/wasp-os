import fonts
import widgets

DIGITS = (
        fonts.clock_0,
        fonts.clock_1,
        fonts.clock_2,
        fonts.clock_3,
        fonts.clock_4,
        fonts.clock_5,
        fonts.clock_6,
        fonts.clock_7,
        fonts.clock_8,
        fonts.clock_9
)

class ClockApp(object):

    def __init__(self):
        self.on_screen = ( -1, -1 )
        self.meter = widgets.BatteryMeter()

    def draw(self, watch):
        display = watch.display

        display.fill(0)
        display.rleblit(fonts.clock_colon, pos=(2*48, 80), fg=0xb5b6)
        self.on_screen = ( -1, -1 )
        self.update(watch)
        self.meter.draw()

    def update(self, watch):
        now = watch.rtc.get_time()
        if now[0] == self.on_screen[0] and now[1] == self.on_screen[1]:
            if now[1] % 2 == 0:
                self.meter.update()
            return False

        display = watch.display
        display.rleblit(DIGITS[now[1]  % 10], pos=(4*48, 80))
        display.rleblit(DIGITS[now[1] // 10], pos=(3*48, 80), fg=0xbdb6)
        display.rleblit(DIGITS[now[0]  % 10], pos=(1*48, 80))
        display.rleblit(DIGITS[now[0] // 10], pos=(0*48, 80), fg=0xbdb6)
        self.on_screen = now

        self.meter.update()
        return True
