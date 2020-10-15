import watch
from ubluepy import Service, Characteristic, UUID, Peripheral, constants
import struct


_BATT_SERV_UUID = UUID("0x180F")  # Battery Service
_BATT_CHAR_UUID = UUID("0x2A19")  # Battery Level Characteristic

_BATT_SERVICE = Service(_BATT_SERV_UUID)

batt_props = Characteristic.PROP_READ
batt_attrs = Characteristic.ATTR_CCCD
_BATT_CHAR = Characteristic(_BATT_CHAR_UUID, props=Characteristic.PROP_READ,
                            attrs=batt_attrs)

_BATT_SERVICE.addCharacteristic(_BATT_CHAR)


periph = Peripheral()


class BleWaspOsProfile:
    def __init__(self, ble=periph):
        self.batt = watch.battery
        self.set_msg = watch.boot_msg
        self._ble = ble
        self._vib = watch.vibrator
        self._servs = _BATT_SERVICE
        self._batt_char = _BATT_CHAR
        self._ble.addService(_BATT_SERVICE)
        self._ble.setConnectionHandler(self.event_handler)

    def update(self):
        self._batt_char.write(struct.pack("B", self.batt.level()))

    def event_handler(self, id, handle, data):

        if id == constants.EVT_GAP_CONNECTED:
            # indicated 'connected'
            self._vib.pulse()

        elif id == constants.EVT_GAP_DISCONNECTED:
            # stop low power timer
            self._vib.pulse()
            # indicate 'disconnected'
            # restart advertisment

        elif id == constants.EVT_GATTS_WRITE:

            pass
