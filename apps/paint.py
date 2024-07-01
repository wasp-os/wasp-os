import wasp

COLORS = {
    "white": 0xffff,
    "red": 0xf800,
    "green": 0x07E0,
    "blue": 0x001F,
    "cyan": 0x07FF,
    "purple": 0x801F,
    "pink": 0xF81F,
    "yellow": 0xFFE0
}
class PaintApp():
    
    NAME="Paint"
    def __init__(self) -> None:
        pass
        
    def foreground(self):
        self.redraw = True
        self.current_index = 0
        self.current_color = COLORS['white']
        wasp.system.request_tick(10)
        wasp.system.request_event(wasp.EventMask.TOUCH | 
                                  wasp.EventMask.SWIPE_LEFTRIGHT | 
                                  wasp.EventMask.SWIPE_UPDOWN)
        self._draw()

    def tick(self, ticks):
        wasp.system.keep_awake() 
        self.update()   
    
    def touch(self, event):
        print(event)
    
    def set_current_color(self, index):
        self.redraw = True
        self.current_index = index
        self.current_color = list(COLORS.values())[index]
    
    def swipe(self, event):
        
        if event[0] == wasp.EventType.RIGHT:
            if self.current_index == len(COLORS.items()) - 1:
                self.set_current_color(0)
            else:
                self.set_current_color(self.current_index + 1)
        elif event[0] == wasp.EventType.LEFT:
            if self.current_index == 0:
                self.set_current_color(len(COLORS.items()) - 1)
            else:
                self.set_current_color(self.current_index - 1)
    
    def update(self):
        if self.redraw:
            self.redraw = False
            self._draw()
        else:

            draw = wasp.watch.drawable
            draw.set_color(self.current_color)
            draw.line(0, 120, 240, 240)
    
    def _draw(self):
        draw = wasp.watch.drawable
        draw.fill()
        draw.set_color(self.current_color)
        
        # Draw colour boxes
        draw.fill(self.current_color, 0, 240 - 25, 25, 25)
        
        i = 0
        for key, item in COLORS.items():
            draw.fill(item, 40 + 25*i, 240 - 25, 25, 25)
            i += 1
                
        
        self.update()