import watch
import manager

class FlashlightApp(object):
    """Trivial flashlight application.

    Shows a pure white screen with the backlight set to maximum.
    """

    def __init__(self):
        self.backlight = None

    def foreground(self, manager, effect=None):
        """Activate the application."""
        self.on_screen = ( -1, -1, -1, -1, -1, -1 )
        self.draw(effect)
        manager.request_tick(1000)

    def background(self):
        """De-activate the application (without losing state)."""
        pass

    def sleep(self):
        return False

    def tick(self, ticks):
        pass

    def draw(self, effect=None):
        """Redraw the display from scratch."""
        display = watch.display
        display.fill(0xffff)
