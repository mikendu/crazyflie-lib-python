import struct
from enum import Enum

from cflib.crtp.crtpstack import CRTPPacket
from cflib.crtp.crtpstack import CRTPPort
from cflib.crazyflie.param import WRITE_CHANNEL

__author__ = 'Bitcraze AB'
__all__ = ['LightController', 'ParameterID', 'RingEffect']

class RingEffect(Enum):
    OFF = 0
    FADE_EFFECT = 14
    TIMING_EFFECT = 17

# Hard coding TOC param ids for now, based on the current firmware
class ParameterID(Enum):
    RING_EFFECT = 181       # uint8_t, <B
    FADE_COLOR = 190        # uint32_t, <L
    FADE_TIME = 191         # float, <f


# TODO - Should move this out of the library into application code
class LightController:
    def __init__(self, crazyflie):
        self.crazyflie = crazyflie

    def set_effect(self, effect):
        if not isinstance(effect, RingEffect):
            raise ValueError("Invalid effect given: " + str(effect))

        packet = self._effect_change(effect.value)
        self.crazyflie.send_packet(packet)

    def set_color(self, r, g, b, time = 0.0, set_effect = False):
        color = (int(r) << 16) | (int(g) << 8) | int(b)
        color_packet = self._fade_color(color)
        time_packet = self._fade_time(time)
        self.crazyflie.send_packet(color_packet)
        self.crazyflie.send_packet(time_packet)
        if set_effect:
            self.crazyflie.send_packet(self._effect_change(RingEffect.FADE_EFFECT))

    def _fade_time(self, duration):
        packet = CRTPPacket()
        packet.set_header(CRTPPort.PARAM, WRITE_CHANNEL)
        packet.data = struct.pack('<H', int(ParameterID.FADE_TIME.value))
        packet.data += struct.pack('<f', float(duration))
        return packet

    def _fade_color(self, color):
        packet = CRTPPacket()
        packet.set_header(CRTPPort.PARAM, WRITE_CHANNEL)
        packet.data = struct.pack('<H', int(ParameterID.FADE_COLOR.value))
        packet.data += struct.pack('<L', int(color))
        return packet

    def _effect_change(self, effect):
        packet = CRTPPacket()
        packet.set_header(CRTPPort.PARAM, WRITE_CHANNEL)
        packet.data = struct.pack('<H', int(ParameterID.RING_EFFECT.value))
        packet.data += struct.pack('<B', int(effect))
        return packet