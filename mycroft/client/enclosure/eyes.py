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

from mycroft.util.log import LOG
from .component import EnclosureComponent, get_duration


class EnclosureEyes(EnclosureComponent):
    """
    Listens to enclosure commands for Mycroft's Eyes.

    Performs the associated command on Arduino by writing on the Serial port.
    """
    def __init__(self, ws, writer):
        super(EnclosureEyes, self).__init__(ws, writer)
        self.pixels = [[0] * 12, [0] * 12]
        self.eye_color = 0

    def init_events(self):
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
        self.ws.on('enclosure.eyes.status', self.status)

    def set_state(self, command_string):
        parts = command_string.split('=')
        command = parts[0]
        args = parts[1].split(',') if len(parts) > 1 else None
        if command == 'eyes.set':
            self.pixels[int(args[0]) // 12][int(args[0]) % 12] = int(args[1])
            LOG.info(self.pixels[0])
        elif command == 'eyes.color':
            self.eye_color = int(args[0])
        elif command in ['eyes.reset', 'eyes.blink']:
            self.pixels = [[self.eye_color] * 12, [self.eye_color] * 12]
            self.state = (command, args)
        elif command == 'eyes.volume':
            self.pixels = [
                [self.eye_color if i < args[0] else 0 for i in range(12)],
                [self.eye_color if i < args[0] else 0 for i in range(12)]
            ]
        self.state = (command, args, self.pixels)

    def status(self, event):
        LOG.info('REPORTING STATUS!')
        try:
            self.ws.emit(event.response({'state': self.state}))
        except Exception as e:
            LOG.exception(e)
        LOG.info('STATUS REPORTED!!')

    def on(self, event=None):
        duration = get_duration(event)
        self.queue_up("eyes.on", event.data['timestamp'], duration)

    def off(self, event=None):
        duration = get_duration(event)
        self.queue_up("eyes.off", event.data['timestamp'], duration)

    def blink(self, event=None):
        side = "b"
        duration = get_duration(event, 0.5)
        if event and event.data:
            side = event.data.get("side", side)
        self.queue_up("eyes.blink=" + side, event.data['timestamp'], duration)

    def narrow(self, event=None):
        duration = get_duration(event, 0.3)
        self.queue_up("eyes.narrow", event.data['timestamp'], duration)

    def look(self, event=None):
        duration = get_duration(event)
        if event and event.data:
            side = event.data.get("side", "")
            self.queue_up("eyes.look=" + side, event.data['timestamp'],
                          duration)

    def color(self, event=None):
        r, g, b = 255, 255, 255
        duration = get_duration(event)
        if event and event.data:
            r = int(event.data.get("r", r))
            g = int(event.data.get("g", g))
            b = int(event.data.get("b", b))
        color = (r * 65536) + (g * 256) + b
        self.queue_up("eyes.color=" + str(color), event.data['timestamp'],
                      duration)

    def set_pixel(self, event=None):
        idx = 0
        r, g, b = 255, 255, 255
        duration = get_duration(event, 0.05)
        if event and event.data:
            idx = int(event.data.get("idx", idx))
            r = int(event.data.get("r", r))
            g = int(event.data.get("g", g))
            b = int(event.data.get("b", b))
        color = (r * 65536) + (g * 256) + b
        self.queue_up("eyes.set=" + str(idx) + "," + str(color),
                      event.data['timestamp'], duration)

    def fill(self, event=None):
        amount = 0
        duration = get_duration(event)
        if event and event.data:
            percent = int(event.data.get("percentage", 0))
            amount = int(round(23.0 * percent / 100.0))
        self.queue_up("eyes.fill=" + str(amount), event.data['timestamp'],
                      duration)

    def brightness(self, event=None):
        level = 30
        duration = get_duration(event)
        if event and event.data:
            level = event.data.get("level", level)
        self.queue_up("eyes.level=" + str(level), event.data['timestamp'],
                      duration)

    def volume(self, event=None):
        volume = 4
        duration = get_duration(event)
        if event and event.data:
            volume = event.data.get("volume", volume)
        self.queue_up("eyes.volume=" + str(volume), event.data['timestamp'],
                      duration)

    def reset(self, event=None):
        duration = get_duration(event)
        self.queue_up("eyes.reset", event.data['timestamp'], duration)

    def spin(self, event=None):
        duration = get_duration(event)
        self.queue_up("eyes.spin", event.data['timestamp'], duration)

    def timed_spin(self, event=None):
        length = 5000
        duration = get_duration(event)
        if event and event.data:
            length = event.data.get("length", length)
        self.queue_up("eyes.spin=" + str(length), event.data['timestamp'],
                      duration)
