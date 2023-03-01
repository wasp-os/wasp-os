import watch
import sys

from micropython import const

_WRIST_TILT_Y_SWITCH_THRESHOLD = const(-768)
_WRIST_TILT_SPEED_MODIFIER = const(8)
_WRIST_TILT_X_THRESHOLD = const(512)
_WRIST_TILT_Y_THRESHOLD = const(0)
_WRIST_TILT_REQUIRED_SPEED = const(256)

_POLL_INTERVAL_MS = const(100)

class AccelGestureEvent():
    """Enumerated ids for accelerometer-based gesture events
    """
    NONE = const(0)
    WRIST_TILT = const(1)

class MotionDetector():
    """Handles motion detection using either hardware-backed events
    or algorithms implemented in software
    """

    def __init__(self):
        self._last_x = sys.maxsize
        self._last_y = sys.maxsize
        self._last_z = sys.maxsize
        self._poll_expiry = 0
        self._event = AccelGestureEvent.NONE
        watch.accel.reset()

    def get_gesture_event(self):
        return self._event

    def reset_gesture_event(self):
        self._event = AccelGestureEvent.NONE

    def update(self):
        now = watch.rtc.get_uptime_ms()
        if now < self._poll_expiry:
            return

        self._poll_expiry = now + _POLL_INTERVAL_MS

        # Prioritize hardware-based gestures
        # TODO: Allow drivers to specify *which* gestures they can detect
        if watch.accel.hardware_gesture_available:
            self._event = watch.accel.get_gesture_event()
            watch.accel.reset_gesture_event()
            return

        (x, y, z) = watch.accel.accel_xyz()

        if self._last_x == sys.maxsize:
            self._last_x = x
            self._last_y = y
            self._last_z = z
            return

        if self._detect_wrist_tilt(x, y, z):
            self._event = AccelGestureEvent.WRIST_TILT

        self._last_x = x
        self._last_y = y
        self._last_z = z

    def _detect_wrist_tilt(self, x, y, z):
        # To make our code match InfiniTime, flip the coordinate system first
        (x, y, z) = (-x, -y, -z)
        (last_y, last_z) = (-self._last_y, -self._last_z)

        delta_y = y - last_y
        delta_z = z - last_z

        if abs(x) > _WRIST_TILT_X_THRESHOLD or y > _WRIST_TILT_Y_THRESHOLD:
            return False

        if y < _WRIST_TILT_Y_SWITCH_THRESHOLD:
            return delta_z > _WRIST_TILT_REQUIRED_SPEED

        if z > 0:
            return delta_y > (_WRIST_TILT_REQUIRED_SPEED + (y - delta_y / 2) / _WRIST_TILT_SPEED_MODIFIER)

        return delta_y < (-_WRIST_TILT_REQUIRED_SPEED - (y - delta_y / 2) / _WRIST_TILT_SPEED_MODIFIER)
