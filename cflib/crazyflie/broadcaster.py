
"""
Used for sending high level setpoints to the Crazyflie
"""
import re

from threading import Event
from cflib.crazyflie import HighLevelCommander, LightController
from cflib.crtp.cflinkcppdriver import CfLinkCppDriver
from cflib.crtp.radiodriver import Crazyradio

__author__ = 'Bitcraze AB'
__all__ = ['Broadcaster']

class Broadcaster():

    def __init__(self, channel, datarate = Crazyradio.DR_2MPS):
        self._validate_channel(channel)
        self._validate_datarate(datarate)

        self._uri = self._construct_uri(channel, datarate)
        self._radio = CfLinkCppDriver()
        self._is_link_open = False

        self.high_level_commander = HighLevelCommander(self)
        self.light_controller = LightController(self)

    def open_link(self):
        if (self.is_link_open()):
            raise Exception('Link already open')

        # print('Connecting to %s' % self._uri)
        self._radio.connect(self._uri, None, None)
        self._is_link_open = True

    def __enter__(self):
        self.open_link()
        return self

    def close_link(self):
        if (self.is_link_open()):
            self._radio.close()
            self._is_link_open = False

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close_link()

    def is_link_open(self):
        return self._is_link_open

    def send_packet(self, packet):
        if not self.is_link_open():
            raise Exception('Link is not open')

        self._radio.send_packet(packet)

    def __str__(self):
        return "BroadcastLink <" + str(self._uri)  + ">"

    def _construct_uri(self, channel, datarate):
        return "radiobroadcast://*/" + str(channel) + "/" + self._get_data_rate_string(datarate)

    def _validate_channel(self, channel):
        if channel and (isinstance(channel, int) or channel.is_integer()):
            if channel >= 0 and channel <= 127:
                return
        raise ValueError("Invalid channel: " + str(channel))

    def _validate_datarate(self, datarate):
        if not(datarate == Crazyradio.DR_250KPS or \
            datarate == Crazyradio.DR_1MPS or \
            datarate == Crazyradio.DR_2MPS):
            raise ValueError("Invalid data rate: " + str(datarate))

    def _get_data_rate_string(self, datarate):
        if datarate == Crazyradio.DR_250KPS:
            return '250K'
        elif datarate == Crazyradio.DR_1MPS:
            return '1M'
        elif datarate == Crazyradio.DR_2MPS:
            return '2M'

