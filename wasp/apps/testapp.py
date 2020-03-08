import watch
import widgets
import manager

from draw565 import Draw565

class TestApp():
    """Simple test application.
    """

    def __init__(self):
        self.tests = ('Touch', 'String')
        self.test = self.tests[0]
        self.drawable = Draw565(watch.display)

    def foreground(self, system, effect=None):
        """Activate the application."""
        self.on_screen = ( -1, -1, -1, -1, -1, -1 )
        self.draw(effect)
        system.request_event(manager.EVENT_TOUCH | manager.EVENT_SWIPE_LEFTRIGHT)

    def background(self):
        """De-activate the application (without losing state)."""
        pass

    def sleep(self):
        return False

    def swipe(self, event):
        tests = self.tests
        i = tests.index(self.test) + 1
        if i >= len(tests):
            i = 0
        self.test = tests[i]
        self.draw()

    def touch(self, event):
        draw = self.drawable
        if self.test == 'Touch':
            draw.string('({}, {})'.format(event[1], event[2]),
                    0, 180, width=240)
        elif self.test == 'String':
            watch.display.fill(0, 0, 30, 240, 240-30)
            draw.string("The quick brown", 12, 24+24)
            draw.string("fox jumped over", 12, 24+48)
            draw.string("the lazy dog.", 12, 24+72)
            draw.string("0123456789", 12, 24+120)
            draw.string('!"£$%^&*()', 12, 24+144)

        return True

    def draw(self, effect=None):
        """Redraw the display from scratch."""
        watch.display.fill(0)
        self.drawable.string('{} test'.format(self.test),
                0, 6, width=240)
