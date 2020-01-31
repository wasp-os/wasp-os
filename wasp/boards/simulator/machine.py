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

    def __init__(self, id, direction, value=1):
        self._id = id
        self._value = 0

    def init(self, d, value):
        self.value(value)

    def on(self):
        self.value(1)

    def off(self):
        self.value(0)

    def value(self, v=None):
        if v is None:
            return self._value
        if v:
            print(self._id + ": on")
            self._value = False
        else:
            print(self._id + ": off")
            self._value = True

    def __call__(self, v=None):
        self.value(v)

class PWM(Tracer):
    FREQ_16MHZ = 'FREQ_16MHZ'

class SPI(object):
    def __init__(self, id):
        self._id = id

    def init(self, baudrate=1000000,  polarity=0, phase=0, bits=8, sck=None, mosi=None, miso=None):
        pass

    def write(self, buf):
        print("Sending data: " + str(buf))
