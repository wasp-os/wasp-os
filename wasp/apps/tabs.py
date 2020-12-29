"""Tabbed applications
~~~~~~~~~~~~~~~~~~~~~~

The tabs are used to provide multiple screens in apps.
"""

import wasp

class TabsApp():
    NAME = 'Tabs'

    def __init__(self, tabs=()):
        self.tabs = tabs
        self.current_tab = 0

    def foreground(self):
        """Activate the app"""
        self._redraw()

    def swipe(self, event):
        """Handle switching tabs"""
        mute = wasp.watch.display.mute

        moved = False

        if event[0] == wasp.EventType.LEFT:
            moved = self.current_tab < len(self.tabs) - 1
            self.current_tab = min(len(self.tabs) - 1, self.current_tab + 1)
        elif event[0] == wasp.EventType.RIGHT:
            moved = self.current_tab > 0
            self.current_tab = max(0, self.current_tab - 1)
        if moved:
            mute(True)
            self.draw()
            mute(False)

    def _redraw(self):
        self.current_tab = 0
        self.draw()

    def draw(self):
        numtabs = len(self.tabs)
        tab_width = 240 // numtabs
        draw = wasp.watch.drawable
        draw.reset()
        draw.fill()
        for i, s in enumerate(self.tabs):
            bg = wasp.system.theme('accent-lo')
            if s == self.tabs[self.current_tab]:
                bg = wasp.system.theme('accent-hi')
                draw.reset()
            draw.fill(bg, i * tab_width, 0, tab_width, 24) # Probably shouldn't hardcode string height here....
            draw.set_color(0x0, bg)
            chunks = draw.wrap(s, tab_width)
            draw.string(s[chunks[0]:chunks[1]], i * tab_width, 0)
        draw.reset()
