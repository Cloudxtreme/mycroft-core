# Copyright 2017 Mycroft AI Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from threading import Thread, Lock
import time


class EnclosureEyes(Thread):
    """
    Listens to enclosure commands for Mycroft's Eyes.

    Performs the associated command on Arduino by writing on the Serial port.
    """

    def __init__(self, ws, writer):
        self.ws = ws
        self.writer = writer
        self.__init_events()

        # Setup clearable/inspectable queue
        self.queue_lock = Lock()
        self.__queue = []

        # Start queue handling thread
        self.daemon = True
        self.start()

    def __init_events(self):
        self.ws.on('enclosure.eyes.on', self.on)
        self.ws.on('enclosure.eyes.off', self.off)
        self.ws.on('enclosure.eyes.blink', self.blink)
        self.ws.on('enclosure.eyes.narrow', self.narrow)
        self.ws.on('enclosure.eyes.look', self.look)
        self.ws.on('enclosure.eyes.color', self.color)
        self.ws.on('enclosure.eyes.level', self.brightness)
        self.ws.on('enclosure.eyes.volume', self.volume)
        self.ws.on('enclosure.eyes.spin', self.spin)
        self.ws.on('enclosure.eyes.timedspin', self.timed_spin)
        self.ws.on('enclosure.eyes.reset', self.reset)
        self.ws.on('enclosure.eyes.setpixel', self.set_pixel)
        self.ws.on('enclosure.eyes.fill', self.fill)

    def queue_clear(self):
        with self.queue_lock:
            self.queue = []

    def queue_up(self, command, time=None, owner=None):
        with self.queue_lock:
            self.queue.append((command, time, owner))

    def run(self):
        while self.running:
            with self.queue_lock:
                if len(self.queue) > 0:
                    command, timeout, owner = self.queue.pop()
                    self.writer.write(command)
                    time.sleep(timeout or 0.1)
                else:
                    time.sleep(0.1)

    def clear_queue(self):
        with self.queue_lock:
            self.queue = []

    def on(self, event=None):
        self.queue_up("eyes.on")

    def off(self, event=None):
        self.queue_up("eyes.off")

    def blink(self, event=None):
        side = "b"
        if event and event.data:
            side = event.data.get("side", side)
        self.queue_up("eyes.blink=" + side)

    def narrow(self, event=None):
        self.queue_up("eyes.narrow")

    def look(self, event=None):
        if event and event.data:
            side = event.data.get("side", "")
            self.queue_up("eyes.look=" + side)

    def color(self, event=None):
        r, g, b = 255, 255, 255
        if event and event.data:
            r = int(event.data.get("r", r))
            g = int(event.data.get("g", g))
            b = int(event.data.get("b", b))
        color = (r * 65536) + (g * 256) + b
        self.queue_up("eyes.color=" + str(color))

    def set_pixel(self, event=None):
        idx = 0
        r, g, b = 255, 255, 255
        if event and event.data:
            idx = int(event.data.get("idx", idx))
            r = int(event.data.get("r", r))
            g = int(event.data.get("g", g))
            b = int(event.data.get("b", b))
        color = (r * 65536) + (g * 256) + b
        self.queue_up("eyes.set=" + str(idx) + "," + str(color))

    def fill(self, event=None):
        amount = 0
        if event and event.data:
            percent = int(event.data.get("percentage", 0))
            amount = int(round(23.0 * percent / 100.0))
        self.queue_up("eyes.fill=" + str(amount))

    def brightness(self, event=None):
        level = 30
        if event and event.data:
            level = event.data.get("level", level)
        self.queue_up("eyes.level=" + str(level))

    def volume(self, event=None):
        volume = 4
        if event and event.data:
            volume = event.data.get("volume", volume)
        self.queue_up("eyes.volume=" + str(volume))

    def reset(self, event=None):
        self.queue_up("eyes.reset")

    def spin(self, event=None):
        self.queue_up("eyes.spin")

    def timed_spin(self, event=None):
        length = 5000
        if event and event.data:
            length = event.data.get("length", length)
        self.queue_up("eyes.spin=" + str(length))
