import wasp
import ble

class DisaBLEApp():
    NAME = 'DisaBLE'

    def foreground(self):
        draw = wasp.watch.drawable
        draw.fill()
        ble.disable()
        draw.string('Disabled!', 0, 60, width=240)
