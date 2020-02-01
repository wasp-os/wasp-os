import display

class Tracer(object):
    def __init__(self, *args, **kwargs):
        print(f'{self.__class__.__name__}.__init__{args} {kwargs}')

    def __getattr__(self, name):
        if name.upper() == name:
            return name
        return lambda *args, **kwargs: print(f'{self.__class__.__name__}.{name}{args} {kwargs}')

class ADC(Tracer):
    pass

class Pin(object):
    IN = 'IN'
    OUT = 'OUT'

    def __init__(self, id, direction, value=1, quiet=False):
        self._id = id
        self._value = 0
        self._quiet = quiet

    def init(self, d, value):
        self.value(value)

    def on(self):
        self.value(1)

    def off(self):
        self.value(0)

    def value(self, v=None):
        if v is None:
            if not self._quiet:
                print(f'{self._id}: read {self._value}')
            return self._value
        if v:
            if not self._quiet:
                print(self._id + ": set on")
            self._value = False
        else:
            if not self._quiet:
                print(self._id + ": set off")
            self._value = True

    def __call__(self, v=None):
        self.value(v)

class PWM(Tracer):
    FREQ_16MHZ = 'FREQ_16MHZ'

class SPI(object):
    def __init__(self, id):
        self._id = id
        if id == 0:
            self.sim = display.ST7789Sim()
        else:
            self.sim = None

    def init(self, baudrate=1000000,  polarity=0, phase=0, bits=8, sck=None, mosi=None, miso=None):
        pass

    def write(self, buf):
        if self.sim:
            self.sim.write(buf)
        else:
            print("Sending data: " + str(buf))
