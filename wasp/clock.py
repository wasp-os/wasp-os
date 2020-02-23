import fonts.clock as digits
import widgets

from draw565 import Draw565

DIGITS = (
        digits.clock_0,
        digits.clock_1,
        digits.clock_2,
        digits.clock_3,
        digits.clock_4,
        digits.clock_5,
        digits.clock_6,
        digits.clock_7,
        digits.clock_8,
        digits.clock_9
)

MONTH = 'JanFebMarAprMayJunJulAugSepOctNovDec'

class ClockApp(object):

    def __init__(self):
        self.on_screen = ( -1, -1, -1, -1, -1, -1 )
        self.meter = widgets.BatteryMeter()

    def draw(self, watch):
        display = watch.display

        display.fill(0)
        display.rleblit(digits.clock_colon, pos=(2*48, 80), fg=0xb5b6)
        self.on_screen = ( -1, -1, -1, -1, -1, -1 )
        self.update(watch)
        self.meter.draw()

    def update(self, watch):
        now = watch.rtc.get_localtime()
        if now[3] == self.on_screen[3] and now[4] == self.on_screen[4]:
            if now[5] != self.on_screen[5]:
                self.meter.update()
                self.on_screen = now
            return False

        display = watch.display
        display.rleblit(DIGITS[now[4]  % 10], pos=(4*48, 80))
        display.rleblit(DIGITS[now[4] // 10], pos=(3*48, 80), fg=0xbdb6)
        display.rleblit(DIGITS[now[3]  % 10], pos=(1*48, 80))
        display.rleblit(DIGITS[now[3] // 10], pos=(0*48, 80), fg=0xbdb6)
        self.on_screen = now

        draw = Draw565(display)
        month = now[1] - 1
        month = MONTH[month*3:(month+1)*3]
        draw.string('{}-{}-{}'.format(now[2], month, now[0]),
                0, 180, width=240)

        self.meter.update()
        return True
