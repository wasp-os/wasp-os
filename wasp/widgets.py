import icons
import watch

class BatteryMeter(object):
    def __init__(self):
        self.level = -2

    def draw(self):
        self.level = -2
        self.update()
        
    def update(self):
        icon = icons.battery
        draw = watch.drawable

        if watch.battery.charging():
            if self.level != -1:
                draw.rleblit(icon, pos=(239-icon[0], 0), fg=0x7bef)
                self.level = -1
        else:
            level = watch.battery.level()
            if level == self.level:
                return

            if level > 96:
                h = 24
                rgb = 0x07e0
            else:
                h = level // 4

                green = level // 3
                red = 31-green
                rgb = (red << 11) + (green << 6)

            if (level > 5) ^ (self.level > 5):
                if level  > 5:
                    draw.rleblit(icon, pos=(239-icon[0], 0), fg=0x7bef)
                else:
                    rgb = 0xf800
                    draw.rleblit(icon, pos=(239-icon[0], 0), fg=0xf800)

            x = 239 - 30
            w = 16
            if 24 - h:
                draw.fill(0, x, 14, w, 24 - h)
            if h:
                draw.fill(rgb, x, 38 - h, w, h)

            self.level = level
