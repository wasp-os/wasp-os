import watch
import widgets
import manager

from draw565 import Draw565

class TouchTestApp(object):
    """Simple application to visualize touch events.
    """

    def __init__(self):
        pass

    def foreground(self, system, effect=None):
        """Activate the application."""
        self.on_screen = ( -1, -1, -1, -1, -1, -1 )
        self.draw(effect)
        system.request_event(manager.EVENT_TOUCH)

    def background(self):
        """De-activate the application (without losing state)."""
        pass

    def sleep(self):
        return False

    def touch(self, event):
        draw = Draw565(watch.display)
        draw.string('({}, {})'.format(event[1], event[2]),
                0, 180, width=240)
        return True

    def draw(self, effect=None):
        """Redraw the display from scratch."""
        watch.display.fill(0)
