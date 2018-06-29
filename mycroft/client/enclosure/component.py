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
from abc import abstractmethod
from threading import Thread, Lock
import time


def get_duration(msg, default=None):
    if msg and msg.data:
        return msg.data.get('duration', 0.05)
    else:
        return 0.05


class EnclosureComponent(Thread):
    def __init__(self, ws, writer):
        super(EnclosureComponent, self).__init__()
        self.ws = ws
        self.writer = writer
        self.init_events()

        self.state = None
        # Setup clearable/inspectable queue
        self.queue_lock = Lock()
        self.__queue = []

        # Start queue handling thread
        self.running = True
        self.daemon = True
        self.start()
        LOG.info('Enclosure Component inited')

    def queue_clear(self):
        with self.queue_lock:
            self.__queue = []

    def queue_up(self, command, timestamp, time=None, owner=None):
        with self.queue_lock:
            self.__queue.insert(0, (command, time, owner, timestamp))
            self.__queue = sorted(self.__queue, key=lambda l: l[3])
            self.__queue.reverse()

    def run(self):
        while self.running:
            with self.queue_lock:
                if len(self.__queue) > 0:
                    command, timeout, owner, _ = self.__queue.pop()
                    self.writer.write(command)
                    try:
                        self.set_state(command)
                    except Exception as e:
                        LOG.exception(e)
                    LOG.debug((time.time(), timeout or 0.05))
                    time.sleep(timeout or 0.05)
                else:
                    time.sleep(0.05)
