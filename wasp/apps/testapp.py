import watch
import widgets
import manager
import machine

class TestApp():
    """Simple test application.
    """

    def __init__(self):
        self.tests = ('Touch', 'String')
        self.test = self.tests[0]

    def foreground(self, system, effect=None):
        """Activate the application."""
        self.on_screen = ( -1, -1, -1, -1, -1, -1 )
        self.draw(effect)
        system.request_event(manager.EVENT_TOUCH | manager.EVENT_SWIPE_UPDOWN)

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
        draw = watch.drawable
        if self.test == 'Touch':
            draw.string('({}, {})'.format(event[1], event[2]),
                    0, 108, width=240)
        elif self.test == 'String':
            draw.fill(0, 0, 30, 240, 240-30)
            t = machine.Timer(id=1, period=8000000)
            t.start()
            draw.string("The quick brown", 12, 24+24)
            draw.string("fox jumped over", 12, 24+48)
            draw.string("the lazy dog.", 12, 24+72)
            draw.string("0123456789", 12, 24+120)
            draw.string('!"£$%^&*()', 12, 24+144)
            elapsed = t.time()
            t.stop()
            del t
            draw.string('{}s'.format(elapsed / 1000000), 12, 24+192)

        return True

    def draw(self, effect=None):
        """Redraw the display from scratch."""
        watch.display.mute(True)
        watch.drawable.fill()
        watch.drawable.string('{} test'.format(self.test),
                0, 6, width=240)
        watch.display.mute(False)
