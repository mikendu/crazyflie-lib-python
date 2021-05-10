# -*- coding: utf-8 -*-
#
# ,---------,       ____  _ __
# |  ,-^-,  |      / __ )(_) /_______________ _____  ___
# | (  O  ) |     / __  / / __/ ___/ ___/ __ `/_  / / _ \
# | / ,--'  |    / /_/ / / /_/ /__/ /  / /_/ / / /_/  __/
#    +------`   /_____/_/\__/\___/_/   \__,_/ /___/\___/
#
# Copyright (C) 2019 - 2020 Bitcraze AB
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, in version 3.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
import logging

from .memory_element import MemoryElement

logger = logging.getLogger(__name__)


class LEDTimingsDriverMemory(MemoryElement):
    """Memory interface for using the LED-ring mapped memory for setting RGB
       values over time. To upload and run a show sequence of
       the LEDs in the ring"""

    def __init__(self, id, type, size, mem_handler):
        super(LEDTimingsDriverMemory, self).__init__(id=id,
                                                     type=type,
                                                     size=size,
                                                     mem_handler=mem_handler)
        self._update_finished_cb = None
        self._write_finished_cb = None

        self.timings = []

    def add(self, duration_seconds, r, g, b):
        self.timings.append({
            'duration': duration_seconds,
            'r': r,
            'g': g,
            'b': b
        })

    def write_data(self, write_finished_cb):
        if write_finished_cb is not None:
            self._write_finished_cb = write_finished_cb

        data = []
        for timing in self.timings:
            # Convert duration from seconds to multiples of 1/100th of a second
            # This gets capped at 65,535 (two bytes)
            time_in_secs = timing['duration']
            time = int(round(100.0 * time_in_secs)) & 0xFFFF
            time_upper = time >> 8
            time_lower = time & 0xFF

            # In order to fit all the LEDs in one radio packet RGB565 is used
            # to compress the colors. The calculations below converts 3 bytes
            # RGB into 2 bytes RGB565. Then shifts the value of each color to
            # LSB, applies the intensity and shifts them back for correct
            # alignment on 2 bytes.
            R5 = ((int)((((int(timing['r']) & 0xFF) * 249 + 1014) >> 11)
                        & 0x1F))
            G6 = ((int)((((int(timing['g']) & 0xFF) * 253 + 505) >> 10)
                        & 0x3F))
            B5 = ((int)((((int(timing['b']) & 0xFF) * 249 + 1014) >> 11)
                        & 0x1F))
            led = (int(R5) << 11) | (int(G6) << 5) | (int(B5) << 0)
            led_upper = led >> 8
            led_lower = led & 0xFF

            current_buffer = [time_upper, time_lower, led_upper, led_lower]
            data += current_buffer

        data += [0, 0, 0, 0]
        self.mem_handler.write(self, 0x00, bytearray(data), flush_queue=True)

    def write_raw(self, data, write_finished_cb):
        if write_finished_cb is not None:
            self._write_finished_cb = write_finished_cb
        self.mem_handler.write(self, 0x00, bytearray(data), flush_queue=True)


    def write_done(self, mem, addr):
        if mem.id == self.id and self._write_finished_cb:
            self._write_finished_cb(self, addr)
            self._write_finished_cb = None

    def disconnect(self):
        self._update_finished_cb = None
        self._write_finished_cb = None
