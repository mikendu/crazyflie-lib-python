import struct
from cflib.crtp.crtpstack import CRTPPacket
from cflib.crtp.crtpstack import CRTPPort
from cflib.crazyflie.param import WRITE_CHANNEL

__author__ = 'Bitcraze AB'
__all__ = ['LedUtils']

# TODO - Should move this out of the library into application code
class LedUtils:

    # Hard coding TOC param ids for now
    RING_EFFECT = 157       # uint8_t, <B
    FADE_COLOR = 166        # uint32_t, <L
    FADE_TIME = 167         # float, <f

    @staticmethod
    def ring_effect(effect):
        packet = CRTPPacket()
        packet.set_header(CRTPPort.PARAM, WRITE_CHANNEL)
        packet.data = struct.pack('<H', LedUtils.RING_EFFECT)
        packet.data += struct.pack('<B', int(effect))
        # print("Packet: ", packet)
        return packet

    @staticmethod
    def fade_time(duration):
        packet = CRTPPacket()
        packet.set_header(CRTPPort.PARAM, WRITE_CHANNEL)
        packet.data = struct.pack('<H', LedUtils.FADE_TIME)
        packet.data += struct.pack('<f', float(duration))
        return packet

    @staticmethod
    def fade_color(color):
        packet = CRTPPacket()
        packet.set_header(CRTPPort.PARAM, WRITE_CHANNEL)
        packet.data = struct.pack('<H', LedUtils.FADE_COLOR)
        packet.data += struct.pack('<L', int(color))
        return packet