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

""" DisplayManager

This module is depreciated and only remains for backwards compatibility,
use mycroft.enclosure.display_manager.
"""
from mycroft.enclosure import display_manager
from mycroft.util.log import LOG
LOG.info('mycroft.client.enclosure.display_manager is depeciated '
         'use mycroft.enclosure.display_manager')


def _write_data(dictionary):
    """ Writes the dictionary of state data to the IPC directory.

    Args:
        dictionary (dict): information to place in the 'disp_info' file
    """
    return display_manager._write_data(dictionary)


def _read_data():
    """ Writes the dictionary of state data from the IPC directory.
    Returns:
        dict: loaded state information
    """
    return display_manager._read_data()


def set_active(skill_name):
    """ Sets skill name as active in the display Manager
    Args:
        string: skill_name
    """
    return display_manager.set_active(skill_name)


def get_active():
    """ Get the currenlty active skill from the display manager
    Returns:
        string: The active skill's name
    """
    return display_manager.get_active()


def remove_active():
    """ Clears the active skill """
    return display_manager.remove_active()


def initiate_display_manager_ws():
    """ Initiates the web sockets on the display_manager """
    display_manager.initiate_display_manager_ws()
