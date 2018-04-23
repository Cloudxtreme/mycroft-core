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
#
import time
from .component import EnclosureComponent


class EnclosureMouth(EnclosureComponent):
    """
    Listens to enclosure commands for Mycroft's Mouth.

    Performs the associated command on Arduino by writing on the Serial port.
    """

    def __init__(self, ws, writer):
        super(EnclosureEyes, self).__init__(ws, writer)
        self.__init_events()

    def __init_events(self):
        self.ws.on('enclosure.mouth.reset', self.reset)
        self.ws.on('enclosure.mouth.talk', self.talk)
        self.ws.on('enclosure.mouth.think', self.think)
        self.ws.on('enclosure.mouth.listen', self.listen)
        self.ws.on('enclosure.mouth.smile', self.smile)
        self.ws.on('enclosure.mouth.viseme', self.viseme)
        self.ws.on('enclosure.mouth.text', self.text)
        self.ws.on('enclosure.mouth.display', self.display)
        self.ws.on('enclosure.weather.display', self.display_weather)

    def reset(self, event):
        self.queue_up("mouth.reset", event.data['timestamp'])

    def talk(self, event):
        self.queue_up("mouth.talk", event.data['timestamp'])

    def think(self, event):
        self.queue_up('mouth.think', event.data['timestamp'])

    def listen(self, event):
        self.queue_up('mouth.listen', event.data['timestamp'])

    def smile(self, event):
        self.queue_up('mouth.smile', event.data['timestamp'])

    def viseme(self, event):
        if event and event.data:
            code = event.data.get('code')
            time_until = event.data.get('until')
            # Skip the viseme if the time has expired.  This helps when a
            # system glitch overloads the bus and throws off the timing of
            # the animation timing.
            if code and (not time_until or time.time() < time_until):
                self.queue_up('mouth.viseme=' + code, event.data['timestamp'])

    def text(self, event):
        text = ""
        if event and event.data:
            text = event.data.get("text", text)
        self.queue_up("mouth.text=" + text, event.data['timestamp'])

    def display(self, event):
        timestamp = event.data['timestamp']
        code = ""
        xOffset = ""
        yOffset = ""
        clearPrevious = ""
        if event and event.data:
            code = event.data.get("img_code", code)
            xOffset = event.data.get("xOffset", xOffset)
            yOffset = event.data.get("yOffset", yOffset)
            clearPrevious = event.data.get("clearPrev", clearPrevious)

        clearPrevious = int(str(clearPrevious) == "True")
        clearPrevious = "cP=" + str(clearPrevious) + ","
        x_offset = "x=" + str(xOffset) + ","
        y_offset = "y=" + str(yOffset) + ","

        message = "mouth.icon=" + x_offset + y_offset + clearPrevious + code
        # Check if message exceeds Arduino's serial buffer input limit 64 bytes
        if len(message) > 60:
            message1 = message[:31]
            message2 = message[31:]
            message1 += "$"
            message2 += "$"
            message2 = "mouth.icon=" + message2
            self.queue_up(message1, timestamp, 0.25)
            timestamp += 0.001
            self.queue_up(message2, timestamp, 0.25)
        else:
            self.queue_up(message, timestamp, 0.25)

    def display_weather(self, event=None):
        if event and event.data:
            # Convert img_code to icon
            img_code = event.data.get("img_code", None)
            icon = None
            if img_code == 0:
                # sunny
                icon = "IICEIBMDNLMDIBCEAA"
            elif img_code == 1:
                # partly cloudy
                icon = "IIEEGBGDHLHDHBGEEA"
            elif img_code == 2:
                # cloudy
                icon = "IIIBMDMDODODODMDIB"
            elif img_code == 3:
                # light rain
                icon = "IIMAOJOFPBPJPFOBMA"
            elif img_code == 4:
                # raining
                icon = "IIMIOFOBPFPDPJOFMA"
            elif img_code == 5:
                # storming
                icon = "IIAAIIMEODLBJAAAAA"
            elif img_code == 6:
                # snowing
                icon = "IIJEKCMBPHMBKCJEAA"
            elif img_code == 7:
                # wind/mist
                icon = "IIABIBIBIJIJJGJAGA"

            temp = event.data.get("temp", None)
            if icon is not None and temp is not None:
                icon = "x=2," + icon
                msg = "weather.display=" + str(temp) + "," + str(icon)
                self.queue_up(msg, 2)
