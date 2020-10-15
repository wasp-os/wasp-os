import watch
from ubluepy import Service, Characteristic, UUID, Peripheral, constants
import struct


_BATT_SERV_UUID = UUID("0x180F")  # Battery Service
_BATT_LEVEL_UUID = UUID("0x2A19")  # Battery Level Characteristic

_CURRENT_TIME_SERV_UUID = UUID("0x1805")  # Current Time Service
_DATE_TIME_UUID = UUID("0x2A08")  # Date Time Characteristic

# _BATT_SERVICE = Service(_BATT_SERV_UUID)

_DATE_TIME_SERVICE = Service(_CURRENT_TIME_SERV_UUID)


# _BATT_LEVEL_CHAR = Characteristic(_BATT_LEVEL_UUID, props=Characteristic.PROP_READ,
#                                   attrs=Characteristic.ATTR_CCCD)

# _BATT_SERVICE.addCharacteristic(_BATT_LEVEL_CHAR)

_DATE_TIME_CHAR = Characteristic(_DATE_TIME_UUID, props=Characteristic.PROP_WRITE,
                                 attrs=Characteristic.ATTR_CCCD)

_DATE_TIME_SERVICE.addCharacteristic(_DATE_TIME_CHAR)

periph = Peripheral()


class BleWaspOSProfile:
    def __init__(self, ble=periph, name="wasp-ble"):
        self.batt = watch.battery
        self.set_msg = watch.boot_msg
        self._ble = ble
        self._vib = watch.vibrator
        self._rtc = watch.rtc
        self._name = name
        # self._servs = _BATT_SERVICE
        # self._batt_char = _BATT_LEVEL_CHAR
        self._datetime_char = _DATE_TIME_CHAR
        # self._ble.addService(_BATT_SERVICE)
        self._ble.addService(_DATE_TIME_SERVICE)
        self._ble.setConnectionHandler(self.event_handler)
        self._ble.advertise_stop()
        self._ble.advertise(device_name=name, services=[_DATE_TIME_SERVICE])

    def update(self):
        # self._batt_char.write(struct.pack("B", self.batt.level()))
        pass

    def event_handler(self, id, handle, data):

        if id == constants.EVT_GAP_CONNECTED:
            # indicated 'connected'
            self._ble.advertise_stop()
            self._vib.pulse()

        elif id == constants.EVT_GAP_DISCONNECTED:
            # stop low power timer
            self._vib.pulse()
            self._ble.advertise(device_name=self._name, services=[_DATE_TIME_SERVICE])
            # indicate 'disconnected'
            # restart advertisment

        elif id == constants.EVT_GATTS_WRITE:
            try:
                year, month, day, hour, minute, second = struct.unpack('HBBBBB', data)
                self._rtc.set_localtime((year, month, day, hour, minute, second))
            except Exception as e:
                self.set_msg(e)
