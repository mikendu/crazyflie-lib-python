
"""
Used for sending high level setpoints to the Crazyflie
"""
import re

from threading import Event
from cflib.crazyflie import HighLevelCommander
from cflib.crtp.cflinkcppdriver import CfLinkCppDriver

__author__ = 'Bitcraze AB'
__all__ = ['Broadcaster']


class Broadcaster():

    ADDRESS_PATTERN = re.compile("radio://(\d|\*)/\d{1,2}/(250K|1M|2M)/broadcast")

    def __init__(self, uri):
        if not Broadcaster.ADDRESS_PATTERN.match(uri):
            raise ValueError("Invalid broadcast uri: " + str(uri))

        self._uri = uri
        self._radio = CfLinkCppDriver()
        self._is_link_open = False

        self.high_level_commander = HighLevelCommander(self)

    def open_link(self):
        if (self.is_link_open()):
            raise Exception('Link already open')

        print('Connecting to %s' % self._uri)
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
        return "BroadcastLink <" + str(self.uri)  + ">"
