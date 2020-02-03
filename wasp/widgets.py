import icons
import watch

class BatteryMeter(object):
    def __init__(self):
        self.level = None

    def draw(self):
        display = watch.display
        icon = icons.battery

        watch.display.rleblit(icon, pos=(239-icon[0], 0), fg=0x7bef)
        self.level = -1
        self.update()
        
    def update(self):
        if watch.battery.charging():
            if self.level != -1:
                icon = icons.battery
                watch.display.rleblit(icon, pos=(239-icon[0], 0), fg=0x7bef)
                self.level = -1
        else:
            level = watch.battery.level()
            if level == self.level:
                return
            self.level = level
            x = 239 - 31
            w = 18

            # Use the level to work out the correct height
            if level == 100:
                h = 26
            else:
                h = level // 4

            # Use the level to figure out the right color
            if level > 96:
                rgb = 0x07e0
            else:
                green = level // 3
                red = 31-green
                rgb = (red << 11) + (green << 6)

            if 26 - h:
                watch.display.fill(0, x, 13, 18, 26 - h)
            if h:
                watch.display.fill(rgb, x, 39 - h, 18, h)

